# Python libraries to be installed:

  $ pip3 install pandas
  
  $ pip3 install boto3
  
  $ pip3 install requests
  


# How-to:

$ git clone https://github.com/karolnedza/list_gateways.git .

$ chmod +x list_gw.py

$ ./list_gw.py

Enter Controller IP: 3.215.237.187
Enter Controller username: admin
Enter Controller password:
Enter AWS Access Key: AKIAXM2HB5MPLX2YS3Q3
Enter AWS Secret Key:

Creating report for:  aws-spoke-gw-2
Creating report for:  on-prem-spoke-1
Creating report for:  aws-spoke-gw-1
Creating report for:  on-prem-gw
Creating report for:  aws-spoke-gw-3
Creating report for:  aviatrix-transit-gw-us-east-1
Creating report for:  aviatrix-transit-gw-us-east-1-hagw
Creating report for:  avtx-tgw-migration
Created file gw_list.html
Created file gw_list.csv


# To resize or/and replace GW please uncomment functions

resize_instance(controller, cid, instances_to_resize)
replace_instance(controller, cid, instances_to_replace)
