import boto3
import click
from config import Config
from custom_methods import *

@click.command()
@click.option('--restore_time', required=True, help='The point-in-time to restore to in the format of "YYYY-MM-DDTHH:MM:SS".')
@click.option('--service', required=True, help='The temporary ID for the restored cluster.')
@click.option('--environment', required=True, help='The temporary ID for the restored cluster.')
# restore_db_cluster_to_point_in_time(service,restore_,environment)time:

def restore_db_cluster_to_point_in_time(service,restore_time,environment):
       
        print("test")
        client = boto3.client('docdb')        
        new_restored_cluster_identifier = "new-cluster-identifier-0" + service        
        config_obj = Config(environment, service)
        source_cluster_id = config_obj.config[environment][service]["cluster-identifier"]
        region = config_obj.config[environment]["region"]
        Tags ={
                        # 'project': service,
                        # 'environment': environment,
                        # 'region': region
               }
                
        response = restore_db_cluster_to_pitr(client,new_restored_cluster_identifier,source_cluster_id,restore_time,Tags)
        cluster_info = client.describe_db_clusters(DBClusterIdentifier=source_cluster_id)
        for db_cluster in cluster_info['DBClusters']:
        # Get the list of members in the current DB cluster
            db_cluster_members = db_cluster['DBClusterMembers']
    
            # Loop through the list of members in the current DB cluster
            for member in db_cluster_members:
                # Get the DBInstanceIdentifier of the current member
                old_db_instance_identifier = member['DBInstanceIdentifier']
        
                # Do something with the DBInstanceIdentifier
                print(old_db_instance_identifier)

                instance_info = describe_db_instance(client,old_db_instance_identifier)

                new_restored_instance_identifier = "new-cluster-instance-0" + service
                # old_instance_identifier = "docdb-api-cluster"
                engine = 'docdb'
                temp_cluster_identifier = 'temp-' + source_cluster_id
                temp_instance_identifier = 'temp-' + old_db_instance_identifier

                restore_instance_from_snapshot(
                    client, old_db_instance_identifier,new_restored_instance_identifier, new_restored_cluster_identifier, engine)

                rename_cluster_name(client, source_cluster_id, temp_cluster_identifier)
                rename_db_instance(client, old_db_instance_identifier, temp_instance_identifier)
                wait_for_db_instance_available(client, new_restored_instance_identifier)

                # Rename newly created cluster id and instance id to original names
                rename_cluster_name(client, new_restored_cluster_identifier,
                            source_cluster_id)
                rename_db_instance(client, new_restored_instance_identifier,
                           old_db_instance_identifier)
                
                print(response)

if __name__ == "__main__":
    # cli()
    restore_db_cluster_to_point_in_time()

