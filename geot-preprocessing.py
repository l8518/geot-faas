# Databricks notebook source
in_container_name="adb"
out_container_name="adbout"
storage_account_name="gtbfcore"
in_mount_name="adb"
out_mount_name="adbout"

conf_key=f"fs.azure.account.key.{storage_account_name}.blob.core.windows.net"
# scope_name=
# key_name=
key="5rrNjSFuXWtBO+/9rn2abDLCa4iDJnYSK6TYbUbiyewvpGePX6tw/hOY7izEpz4JeD480kQerh8fASAJFtS/qQ=="

# dbutils.secrets.get(scope = scope_name, key = key_name)

if not any(x.mountPoint == f"/mnt/{in_mount_name}" for x in dbutils.fs.mounts()):
    dbutils.fs.mount(
      source = f"wasbs://{in_container_name}@{storage_account_name}.blob.core.windows.net",
      mount_point = f"/mnt/{in_mount_name}",
      extra_configs = {f"{conf_key}":key})
# dbutils.fs.unmount(f"/mnt/{in_mount_name}")
if not any(x.mountPoint == f"/mnt/{out_mount_name}" for x in dbutils.fs.mounts()):
    dbutils.fs.mount(
      source = f"wasbs://{out_container_name}@{storage_account_name}.blob.core.windows.net",
      mount_point = f"/mnt/{out_mount_name}",
      extra_configs = {f"{conf_key}":key})
    
input_parquets = f"dbfs:/mnt/{in_mount_name}"

# COMMAND ----------

import os
dataset = spark.read.parquet(input_parquets)
# org_dataset = spark.read.parquet(input_parquets)

# COMMAND ----------

measure_groups = {
    'South America': {'providers': { 'AWS': ['sa-east-1'], 'AZURE': ['brazilsouth'], 'GCP': ['southamerica-east1']}, 'timezone': 'America/Sao_Paulo'},
    'Canada': {'providers': {'AWS': ['ca-central-1'], 'AZURE': [], 'GCP': ['northamerica-northeast1']}, 'timezone': 'America/Montreal'},
    'East US': { 'providers': {'AWS': ['us-east-1'], 'AZURE': ['eastus'], 'GCP': ['us-east4']}, 'timezone': 'America/New_York'},
    'West US': { 'providers': {'AWS': ['us-west-1', 'us-west-2'], 'AZURE': ['westus', 'westus2'], 'GCP': ['us-west2', 'us-west4']}, 'timezone': 'America/Los_Angeles'},
    'United Kingdom': {'providers': { 'AWS': ['eu-west-2'], 'AZURE': ['uksouth'], 'GCP': ['europe-west2'] }, 'timezone': 'Europe/London'},
    'Germany': { 'providers': { 'AWS': ['eu-central-1'], 'AZURE': ['germanywestcentral'], 'GCP': ['europe-west3']}, 'timezone': 'Europe/Berlin'},
    'India': { 'providers': { 'AWS': ['ap-south-1'], 'AZURE': ['centralindia'], 'GCP': ['asia-south1'] }, 'timezone': 'Asia/Kolkata'},
    'Japan': { 'providers': { 'AWS': ['ap-northeast-1'], 'AZURE': ['japaneast'], 'GCP': ['asia-northeast1'] }, 'timezone': 'Asia/Tokyo'},
    'Australia': { 'providers': { 'AWS': ['ap-southeast-2'],'AZURE': ['australiaeast'],'GCP': ['australia-southeast1']},'timezone': 'Australia/Sydney'}
}

# COMMAND ----------

import pyspark.sql.functions as f

# Turn dataset into datetime:
# dataset['driver_invocation'] = pd.to_datetime(dataset['driver_invocation'], format='%Y%m%dT%H%M%S%f')
# dataset['workload_invocation'] = pd.to_datetime(dataset['workload_invocation'], format='%Y%m%dT%H%M%S%f')

format = "yyyyMMdd'T'HHmmssSSS"
dataset = dataset.withColumn("driver_invocation", f.to_timestamp("driver_invocation", format))
dataset = dataset.withColumn("workload_invocation", f.to_timestamp("workload_invocation", format))

# COMMAND ----------

import pyspark.sql.functions as f
from pyspark.sql.functions import col

# Preprocessing based on utc:
# dataset['dow_utc'] = dataset['driver_invocation'].dt.day_name()
# dataset['tod_utc'] = dataset['driver_invocation'].dt.strftime('%H%M')
dataset = dataset = dataset.withColumn('tod_utc', f.date_format(col('driver_invocation'), "HHmm"))

# COMMAND ----------

measure_groups

# COMMAND ----------

# for mg in measure_groups:
#    regions = []
#    for provider in measure_groups[mg]['providers']:
#        regions.extend(measure_groups[mg]['providers'][provider])

#    dataset.loc[(dataset['region'].isin(regions)),                'timezone'] = measure_groups[mg]['timezone']
#    dataset.loc[(dataset['region'].isin(regions)), 'measure group'] = mg
import sys

provider_region_mg = {}
for mg in measure_groups:
    for provider in measure_groups[mg]['providers']:
        regions = measure_groups[mg]['providers'][provider]
        for region in regions:
            if provider in provider_region_mg.keys():
                if region in provider_region_mg[provider].keys():
                    raise Exception('Something is wrong')
                else:
                    provider_region_mg[provider][region] = {'mg': mg, 'tz': measure_groups[mg]['timezone']}
            else:
                provider_region_mg[provider] = {}
                provider_region_mg[provider][region] = {'mg': mg, 'tz': measure_groups[mg]['timezone'] }
provider_region_mg

from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def assignMeasureGroup(provider, region):
    return provider_region_mg[provider][region]['mg']
def assignTimezone(provider, region):
    return provider_region_mg[provider][region]['tz']

assignMeasureGroupUDF = udf(assignMeasureGroup, StringType())
assignTimezoneUDF = udf(assignTimezone, StringType())

# COMMAND ----------

dataset = dataset.withColumn("measure_group", assignMeasureGroupUDF("provider", 'region'))
dataset = dataset.withColumn("timezone", assignTimezoneUDF("provider", 'region'))

# COMMAND ----------

import pytz
from datetime import datetime
from pyspark.sql.types import TimestampType

def get_local_dow_of_the_week(driver_invocation, timezone):
    tz = pytz.timezone(timezone)
    utc_dt = driver_invocation.replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(tz)
    return str(local_dt.strftime("%a"))

def get_local_tod_of_the_week(driver_invocation, timezone):
    tz = pytz.timezone(timezone)
    utc_dt = driver_invocation.replace(tzinfo=pytz.utc)
    local_dt = utc_dt.astimezone(tz)
    return local_dt.strftime('%H:%M')

get_local_dow_of_the_weekUdf = udf(get_local_dow_of_the_week)
get_local_tod_of_the_weekUdf = udf(get_local_tod_of_the_week)

dataset = dataset.withColumn("local_dow", get_local_dow_of_the_weekUdf("driver_invocation", 'timezone'))
dataset = dataset.withColumn("local_tod", get_local_tod_of_the_weekUdf("driver_invocation", 'timezone'))
dataset.select("local_dow", "local_tod", "driver_invocation", "timezone").show(truncate=False)

# COMMAND ----------

dataset.columns

# COMMAND ----------

dataset.select('measure_group').distinct().show()

# COMMAND ----------

# dbutils.fs.rm(f"/mnt/{out_mount_name}/dataset.parquet", recurse=True)

# COMMAND ----------

dataset.write.mode('overwrite').partitionBy("provider","region").parquet(f"/mnt/{out_mount_name}/dataset.parquet")

# COMMAND ----------

pdataset = spark.read.parquet(f"/mnt/{out_mount_name}/dataset.parquet")

# COMMAND ----------

pdataset.select('driver_invocation').distinct().count()

# COMMAND ----------

display(pdataset.describe().show())

# COMMAND ----------

# row1 = df1.agg({"x": "max"}).collect()[0]