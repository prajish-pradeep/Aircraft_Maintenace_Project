from confluent_kafka import Consumer
import boto3
import time

def read_config():
    config = {}
    with open("client.properties") as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config

def consume(topic, config, batch_size=1000, rotate_interval_ms=60000, end_timeout=10):
    # Set consumer group ID and offset
    config["group.id"] = "python-group-1"
    config["auto.offset.reset"] = "earliest"  # Ensure starting from the beginning

    consumer = Consumer(config)
    consumer.subscribe([topic])

    # S3 configuration
    s3_bucket_name = 'aircraft-maintenance-data'
    s3_client = boto3.client('s3', region_name='eu-north-1')

    messages = []  # Store messages in a batch
    file_count = 0
    headers = "Unit_ID,Time_in_Cycles,Setting_1,Setting_2,Setting_3,T2,T24,T30,T50,P2,P15,P30,NF,NC,EPR,PS30,PHI,NRF,NRC,BPR,FARB,HTBLEED,NF_DMD,PCRFR_DMD,W31,W32"
    last_rotation_time = time.time()  # Track the last file upload time
    last_message_time = time.time()  # Track the time of the last received message

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Check if we've gone beyond the `end_timeout` without new messages
                if time.time() - last_message_time > end_timeout:
                    break  # Exit loop to process any remaining messages in the `finally` block
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Add message to batch
            csv_line = msg.value().decode('utf-8').replace(" ", ",")
            messages.append(csv_line)
            last_message_time = time.time()  # Reset last message time on new data

            # Check if batch is ready (by size or time interval)
            current_time = time.time()
            if len(messages) >= batch_size or (current_time - last_rotation_time) * 1000 >= rotate_interval_ms:
                # Create file name and content
                file_name = f"aircraft_data_batch_{file_count}.csv"
                file_content = headers + "\n" + "\n".join(messages)

                # Upload to S3
                try:
                    s3_client.put_object(Bucket=s3_bucket_name, Key=file_name, Body=file_content)
                    print(f'Successfully uploaded {file_name} to S3 with {len(messages)} lines')
                except Exception as e:
                    print(f'Failed to upload {file_name} to S3: {e}')

                # Reset for the next batch
                messages = []
                file_count += 1
                last_rotation_time = current_time  # Reset last rotation time

    except KeyboardInterrupt:
        pass
    finally:
        # Upload any remaining messages if they don’t fill the batch size
        if messages:
            file_name = f"aircraft_data_batch_{file_count}.csv"
            file_content = headers + "\n" + "\n".join(messages)
            try:
                s3_client.put_object(Bucket=s3_bucket_name, Key=file_name, Body=file_content)
                print(f'Successfully uploaded final {file_name} to S3 with {len(messages)} lines')
            except Exception as e:
                print(f'Failed to upload {file_name} to S3: {e}')

        consumer.close()

def main():
    config = read_config()
    topic = "maintenance_data"
    consume(topic, config)

if __name__ == "__main__":
    main()
