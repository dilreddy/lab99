import string,random,time,azurerm,json
from azure.storage.table import TableService, Entity

# Define variables to handle Azure authentication
auth_token = azurerm.get_access_token_from_cli()
subscription_id = azurerm.get_subscription_from_cli()

# Define variables with random resource group and storage account names
resourcegroup_name = 'dr'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
storageaccount_name = 'dr'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
location = 'eastus'

###
# Create the a resource group for our demo
# We need a resource group and a storage account. A random name is generated, as each storage account name must be globally unique.
###
response = azurerm.create_resource_group(auth_token, subscription_id, resourcegroup_name, location)
if response.status_code == 200 or response.status_code == 201:
    print('Resource group: ' + resourcegroup_name + ' created successfully.')
else:
    print('Error creating resource group')

# Create a storage account for our demo
response = azurerm.create_storage_account(auth_token, subscription_id, resourcegroup_name, storageaccount_name,  location, storage_type='Standard_LRS')
if response.status_code == 202:
    print('Storage account: ' + storageaccount_name + ' created successfully.')
    time.sleep(2)
else:
    print('Error creating storage account')


###
# Use the Azure Storage Storage SDK for Python to create a Table
###
print('\nLet\'s create an Azure Storage Table to store some data.')
raw_input('Press Enter to continue...')

# Each storage account has a primary and secondary access key.
# These keys are used by aplications to access data in your storage account, such as Tables.
# Obtain the primary storage access key for use with the rest of the demo

response = azurerm.get_storage_account_keys(auth_token, subscription_id, resourcegroup_name, storageaccount_name)
storageaccount_keys = json.loads(response.text)
storageaccount_primarykey = storageaccount_keys['keys'][0]['value']

# Create the Table with the Azure Storage SDK and the access key obtained in the previous step
table_service = TableService(account_name=storageaccount_name, account_key=storageaccount_primarykey)
response = table_service.create_table('itemstable')
if response == True:
    print('Storage Table: itemstable created successfully.\n')
else:
    print('Error creating Storage Table.\n')

time.sleep(1)


###
# Use the Azure Storage Storage SDK for Python to create some entries in the Table
###
print('Now let\'s add some entries to our Table.\nRemember, Azure Storage Tables is a NoSQL datastore, so this is similar to adding records to a database.')
raw_input('Press Enter to continue...')

# Each entry in a Table is called an 'Entity'. 
# Here, we add an entry for first cars with two pieces of data - the name, and the cost
#
# A partition key tracks how like-minded entries in the Table are created and queried.
# A row key is a unique ID for each entity in the partition
# These two properties are used as a primary key to index the Table. This makes queries much quicker.

cars = Entity()
cars.PartitionKey = 'cars'
cars.RowKey = '001'
cars.description = 'Acura'
cars.cost = 30
table_service.insert_entity('itemstable', cars)
print('Created entry for acura...')

cars = Entity()
cars.PartitionKey = 'cars'
cars.RowKey = '002'
cars.description = 'MDX'
cars.cost = 25
table_service.insert_entity('itemstable', cars)
print('Created entry for MDX...')

cars = Entity()
cars.PartitionKey = 'cars'
cars.RowKey = '003'
cars.description = '2017'
cars.cost = 12
table_service.insert_entity('itemstable', cars)
print('Created entry for 2017...\n')

cars = Entity()
cars.PartitionKey = 'cars'
cars.RowKey = '004'
cars.description = 'Grey'
cars.cost = 13
table_service.insert_entity('itemstable', cars)
print('Created entry for Grey...\n')

cars = Entity()
cars.PartitionKey = 'cars'
cars.RowKey = '005'
cars.description = '50000'
cars.cost = 34
table_service.insert_entity('itemstable', cars)
print('Created entry for 50000...\n')

# A partition key tracks how like-minded entries in the Table are created and queried.
# A row key is a unique ID for each entity in the partition
# These two properties are used as a primary key to index the Table. This makes queries much quicker.

coffee = Entity()
coffee.PartitionKey = 'coffeestore'
coffee.RowKey = '005'
coffee.sku = 'BLK203123'
coffee.item = 'starbucks'
coffee.cost = 22.99
table_service.insert_entity('itemstable', coffee)
print('Created entry for a Starbucks...\n')
time.sleep(1)

coffee = Entity()
coffee.PartitionKey = 'coffeestore'
coffee.RowKey = '006'
coffee.sku = 'BLK203143'
coffee.item = 'Lattee'
coffee.cost = 55.99
table_service.insert_entity('itemstable', coffee)
print('Created entry for Lattee...\n')
time.sleep(1)

coffee = Entity()
coffee.PartitionKey = 'coffeestore'
coffee.RowKey = '007'
coffee.sku = 'BLK203163'
coffee.item = 'Small'
coffee.cost = 55.99
table_service.insert_entity('itemstable', coffee)
print('Created entry for Small...\n')
time.sleep(1)

coffee = Entity()
coffee.PartitionKey = 'coffeestore'
coffee.RowKey = '008'
coffee.sku = 'BLK203173'
coffee.item = '2.5'
coffee.cost = 55.99
table_service.insert_entity('itemstable', coffee)
print('Created entry for 2.5...\n')
time.sleep(1)

###
# Use the Azure Storage Storage SDK for Python to query for entities in our Table
###
print('With some data in our Azure Storage Table, we can query the data.\nLet\'s see what the cars menu looks like.')
raw_input('Press Enter to continue...')

# In this query, you define the partition key to search within, and then which properties to retrieve
# Structuring queries like this improves performance as your application scales up and keeps the queries efficient
items = table_service.query_entities('itemstable', filter="PartitionKey eq 'cars'", select='description,cost')
for item in items:
    print('Name: ' + item.description)
    print('Cost: ' + str(item.cost) + '\n')

items = table_service.query_entities('itemstable', filter="PartitionKey eq 'coffeestore'", select='item,cost')
for item in items:
    print('Name: ' + item.item)
    print('Price: ' + str(item.cost) + '\n')

time.sleep(1)


###
# This was a quick demo to see Tables in action.
# Although the actual cost is minimal (fractions of a cent per month) for the three entities we created, it's good to clean up resources when you're done
###
print('\nThis is a basic example of how Azure Storage Tables behave like a database.\nTo keep things tidy, let\'s clean up the Azure Storage resources we created.')
raw_input('Press Enter to continue...')

response = table_service.delete_table('itemstable')
if response == True:
    print('Storage table: itemstable deleted successfully.')
else:
    print('Error deleting Storage Table')

response = azurerm.delete_resource_group(auth_token, subscription_id, resourcegroup_name)
if response.status_code == 202:
    print('Resource group: ' + resourcegroup_name + ' deleted successfully.')
else:
    print('Error deleting resource group.')
