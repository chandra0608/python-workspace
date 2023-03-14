def describe_cluster(client,cluster_identifier):
    response = client.describe_db_clusters(DBClusterIdentifier=cluster_identifier)
    
    #Fetch DBClusterMembers
    # for loop for all the DBInstanceIdentifier ids in DBClusterMembers list
    instance_ids = [instance['DBInstanceIdentifier'] for instance in response['DBClusters'][0]['DBClusterMembers']]
    print("DBClustermembers : ", instance_ids)

    # method in custom_methods to describe cluster and return the dict
    cluster_info = response['DBClusters'][0]
    return cluster_info

def restore_db_cluster_to_pitr(client,NewDBClusterIdentifier,SourceDBClusterIdentifier,RestoreToTime,Tags):
    print("Restoring the Cluster from Snapshot")

    cluster_info = describe_cluster(client,SourceDBClusterIdentifier)
    print("Enabled CW logs export value: " + str(cluster_info))

    response = client.restore_db_cluster_to_point_in_time(
        DBClusterIdentifier=NewDBClusterIdentifier,
        RestoreType='full-copy',
        SourceDBClusterIdentifier=SourceDBClusterIdentifier,
        RestoreToTime=RestoreToTime,
        UseLatestRestorableTime=False,
        Port=27017,
        DBSubnetGroupName=cluster_info['DBSubnetGroup'],
        #VpcSecurityGroupIds=cluster_info['VpcSecurityGroups'],
        Tags=[
            Tags,
        ],
        KmsKeyId=cluster_info['KmsKeyId'],
        DeletionProtection=cluster_info['DeletionProtection'],
        EnableCloudwatchLogsExports=cluster_info['EnabledCloudwatchLogsExports'] if ( 'EnabledCloudwatchLogsExports' in cluster_info) else []
        
    )
    return response

def restore_db_cluster_from_snapshot(client,DBClusterIdentifier,SnapshotIdentifier,Engine):
    print("Restoring the Cluster from Snapshot")
    restored_cluster = client.restore_db_cluster_from_snapshot(
        DBClusterIdentifier=DBClusterIdentifier,
        SnapshotIdentifier=SnapshotIdentifier,
        Engine=Engine
    )

def describe_db_instance(client,instance_identifier):
    response = client.describe_db_instances(DBInstanceIdentifier=instance_identifier)
    instance_info = response['DBInstances'][0]
    return instance_info

def restore_instance_from_snapshot(client,old_instance_identifier,DBInstanceIdentifier,DBClusterIdentifier,Engine):
    print("Restoring the  Instance from Snapshot")
    instance_info = describe_db_instance(client,old_instance_identifier)
    restored_instance = client.create_db_instance(
        DBInstanceIdentifier=DBInstanceIdentifier,
        DBClusterIdentifier=DBClusterIdentifier,
        Engine=Engine,
        DBInstanceClass=instance_info['DBInstanceClass']
        #DBInstanceClass='db.t3.medium'
    )
def wait_for_db_instance_available(client,DBInstanceIdentifier):
    print("Waiting for New cluster & Instance to be available...")
    client.get_waiter('db_instance_available').wait(DBInstanceIdentifier= DBInstanceIdentifier)

def rename_cluster_name(client,DBClusterIdentifier, NewDBClusterIdentifier):
    print("Renaming the Cluster & Instance")
    client.modify_db_cluster(DBClusterIdentifier= DBClusterIdentifier,
        NewDBClusterIdentifier=NewDBClusterIdentifier,
        ApplyImmediately=True
    )
def rename_db_instance(client,DBInstanceIdentifier,NewDBInstanceIdentifier):
    client.modify_db_instance(
        DBInstanceIdentifier=DBInstanceIdentifier,
        NewDBInstanceIdentifier=NewDBInstanceIdentifier,
        ApplyImmediately=True
    )

def get_cluster_identifier(client,snapshot_id):
    response = client.describe_db_cluster_snapshots(DBClusterSnapshotIdentifier=snapshot_id)
    cluster_id = response["DBClusterSnapshots"][0]["DBClusterIdentifier"]
    return cluster_id
