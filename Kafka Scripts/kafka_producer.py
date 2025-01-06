from confluent_kafka import Producer
import os

def read_config():
    # Reads the client configuration from client.properties
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

def split_file_to_chunks(input_file, lines_per_chunk=1000):
    """
    Splits the input CSV file into chunks, each containing lines_per_chunk lines,
    and returns a list of temporary file paths.
    """
    chunk_files = []
    current_chunk = 0
    output_file = None
    
    with open(input_file, 'r') as file:
        for i, line in enumerate(file):
            # Open a new chunk file every `lines_per_chunk` lines
            if i % lines_per_chunk == 0:
                # Close the previous chunk file if it exists
                if output_file is not None:
                    output_file.close()

                # Create and open a new chunk file
                chunk_filename = f"temp_chunk_{current_chunk}.csv"
                chunk_files.append(chunk_filename)
                output_file = open(chunk_filename, 'w')
                current_chunk += 1
                print(f"Starting new chunk file: {chunk_filename}")

            # Write line to the current chunk file
            if output_file:  # Ensure output_file is not None
                output_file.write(line)

        # Close the last file after the loop ends if it exists
        if output_file:
            output_file.close()
    
    return chunk_files

def produce(topic, config, chunk_files):
    # Creates a new producer instance using the provided config
    producer = Producer(config)

    for chunk_file in chunk_files:
        # Read each chunk file line-by-line and send to Kafka
        with open(chunk_file, 'r') as file:
            line_number = 1  # Track line numbers within each file
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace
                if line:  # Check if line is not empty
                    producer.produce(topic, value=line)  # Send line to Kafka topic
                    print(f'Sent line {line_number} from {chunk_file}: {line}')
                    line_number += 1

        # Optionally remove the file after sending to Kafka
        os.remove(chunk_file)
        print(f"Finished sending and removed chunk file: {chunk_file}")

    # Wait for any outstanding messages to be delivered
    producer.flush()

def main():
    config = read_config()  # Read configuration from the properties file
    topic = "maintenance_data"  # Set your Kafka topic name
    csv_file_path = '/Users/prajishpradeep/Downloads/kafka_2.13-3.8.0/kafka_s3_project/dataset/PM_test.csv'

    # Split the original CSV file into chunks of 1000 lines each
    chunk_files = split_file_to_chunks(csv_file_path, lines_per_chunk=1000)
    
    # Produce each chunk file's lines to Kafka
    produce(topic, config, chunk_files)

if __name__ == "__main__":
    main()
