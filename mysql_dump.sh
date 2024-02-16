#!/bin/bash

MYSQL=/usr/bin/mysql
DUMP=/usr/bin/mysqldump
DUMPOPTIONS="-ceqQ --single-transaction --add-drop-table --allow-keywords --skip-lock-tables"
HOST="-h 127.0.0.1"
ACCOUNT="-uUSER  -pPASS $HOST"
DBASES_DIR=/data/mysql_dumps/backup_db
TABLES_DIR=/data/mysql_dumps/backup_db_tables
DATABASES=`$MYSQL $ACCOUNT -Bse 'show databases'|grep -vP 'information_schema test'|grep -v 'test'`

backup_dir=/data/mysql_dumps
mkdir -p $DBASES_DIR
mkdir -p $TABLES_DIR
logfile=$backup_dir/backup.log

echo $DATABASES

rm -f $DBASES_DIR/*.sql.bz2
rm -f $TABLES_DIR/*.sql.bz2

for i in $DATABASES;do
    [ ! -d $TABLES_DIR/$i ] && mkdir -p $TABLES_DIR/$i
    TABLES=`$MYSQL $ACCOUNT -Bse "show tables from $i"|grep -vP 'heap|actual_prices'`
    rm -f $DBASES_DIR/$i.sql.bz2
    for j in $TABLES;do
      $DUMP $ACCOUNT $DUMPOPTIONS $i $j | gzip -1 > $TABLES_DIR/$i/$j.sql.gz
      zcat $TABLES_DIR/$i/$j.sql.gz | bzip2 -c | tee -a $DBASES_DIR/$i.sql.bz2 > $TABLES_DIR/$i/$j.sql.bz2 && rm -f $TABLES_DIR/$i/$j.sql.gz
    done
done