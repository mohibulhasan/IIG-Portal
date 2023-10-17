# Import the requests and csv modules
import requests
import csv
import cactid

# Create a CSV file object
csv_file = open('output.csv', 'w', newline='')
writer = csv.writer(csv_file)

# Create a Cacti API object
cacti = cactid.Cacti('http://192.168.200.45:80', 'noc', 'noc@BSCCL')

# Get a list of devices
devices = cacti.get_devices()

# Iterate over the devices
for device in devices:

    # Get a list of graphs for the device
    graphs = cacti.get_graphs(device['id'])

    # Iterate over the graphs
    for graph in graphs:

        # Get a list of items for the graph
        items = cacti.get_items(graph['id'])

        # Iterate over the items
        for item in items:

            # Write the data to the CSV file
            writer.writerow([item['in'], item['out'], item['title']])

# Close the CSV file object
csv_file.close()
