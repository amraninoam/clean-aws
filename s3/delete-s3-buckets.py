import subprocess
import json

#your region
region="eu-north-99999"

# a function to call command
def call_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = p.communicate()
    return  (output,error)

#query buckets
command = ["aws","s3api","list-buckets","--query","Buckets[].Name"]
output,error=call_command (command)

#loop over buckets
buckets = output.split("\n")
for bucket in buckets:
    bucketName = (bucket.replace(",","").replace("\"","").replace("]","").replace("[","").replace(" ",""))
    if bucketName:
        #get bucket location
        command = ["aws","s3api","get-bucket-location","--bucket",bucketName]
        output,error=call_command (command)
        if not error:
            result = json.loads(output.replace("\n",""))
            if result["LocationConstraint"] == region and "fennec" not in bucketName:
                print ("will delete ", bucketName)
                # trying simple delete
                command = ["aws","s3","rb","s3://"+bucketName, "--force"]
                output,error = call_command (command)
                #bucket not emptry... need to suspend versioning and apply lifecycle rule
                if "(BucketNotEmpty)" in error:
                    # suspending versioning
                    command = ["aws","s3api","put-bucket-versioning","--bucket",bucketName,"--versioning-configuration", "Status=Suspended"]
                    output,error=call_command (command)
                    # apply policy to delete files tomorrow.
                    command = ["aws","s3api","put-bucket-lifecycle-configuration","--bucket",bucketName,"--lifecycle-configuration","file://s3/s3lifecycle.json"] # add delete opbject policy
                    output,error = call_command (command)
