import boto3
import datetime
import jmespath
import time

ec = boto3.client('ec2')
def lambda_handler(event, context):

    images_filter = [{'Name': 'tag-key', 'Values': ['DeleteOn']}]

    found_images = ec.describe_images(Filters=images_filter,
                                      DryRun=False)  # .get('Images', []) #Filters=[{'Name': 'tag:key=DeleteOn'}, ]

    snapshots = ec.describe_snapshots(MaxResults=3000, OwnerIds=['XXXXXX'])['Snapshots']

    today = datetime.datetime.now()

    image_ids = []

    for image in found_images['Images']:
        delete_date = str((jmespath.search("Tags[?Key=='DeleteOn'].Value ", image))).strip("[]''")
        delete_date = time.strptime(delete_date, '%m-%d-%Y')
        if delete_date <= today.timetuple():
            image_ids.append(image['ImageId'])

    print "Found %d AMIs to deregister. They are: %s" % (len(image_ids), image_ids)

    for id in image_ids:
        ec.deregister_image(
            DryRun=False,
            ImageId=id,
        )
        # print('deregistering ami: ' + id)
        for snapshot in snapshots:
            if snapshot['Description'].find(id) > 0:
                print('deleting snapshot ' + snapshot['SnapshotId'])
                ec.delete_snapshot(SnapshotId=snapshot['SnapshotId'])