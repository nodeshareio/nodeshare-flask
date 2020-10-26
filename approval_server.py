import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange, randint
from asyncio_mqtt import Client, MqttError
from time import sleep
import os
from os.path import abspath, join, dirname
import sys
import subprocess
import json
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


broker = os.environ.get('MQTT_BROKER_URL')
port = int(os.environ.get('MQTT_BROKER_PORT'))
print(f'''
    !!!!!!!!! BROKER !!!!!!!!! 
    
    {broker} 
    
    !!!!!!!!!!!!!!!!!!!!!!!!!!!
    ''')
client_id = f'python-mqtt-{randint(0, 1000)}'

sub_topic = "nodeshare/submit"
async def advanced_example():
    # We 💛 context managers. Let's create a stack to help
    # us manage them.
    async with AsyncExitStack() as stack:
        # Keep track of the asyncio tasks that we create, so that
        # we can cancel them on exit
        tasks = set()
        stack.push_async_callback(cancel_tasks, tasks)

        # Connect to the MQTT broker
        client = Client(broker, port=port, username=os.environ.get('MQTT_USERNAME'),password=os.environ.get('MQTT_PASSWORD'), client_id=client_id)
        client._client.tls_set()
        await stack.enter_async_context(client)

        # You can create any number of topic filters
        topic_filters = (
            "nodeshare/#",
            "test/#"
            # 👉 Try to add more filters!
        )
        for topic_filter in topic_filters:
            # Log all messages that matches the filter
            manager = client.filtered_messages(topic_filter)
            messages = await stack.enter_async_context(manager)
            template = f'[topic_filter="{topic_filter}"] Received message: {{}}'
            task = asyncio.create_task(log_messages(messages, template))
            tasks.add(task)



        # Messages that doesn't match a filter will get logged here
        messages = await stack.enter_async_context(client.unfiltered_messages())
        task = asyncio.create_task(log_messages(messages, "[unfiltered] {}"))
        tasks.add(task)

        # Process Submit Messages
        submit_messages = await stack.enter_async_context(client.filtered_messages("nodeshare/submit"))
        task = asyncio.create_task(process_submit(client, submit_messages))
        tasks.add(task)

        # Subscribe to topic(s)
        # 🤔 Note that we subscribe *after* starting the message
        # loggers. Otherwise, we may miss retained messages.
        await client.subscribe(sub_topic)

        # Poll for submissions
        # topics = (
        #     "nodeshare/submit/queue",
        #     # 👉 Try to add more topics!
        # )
        # task = asyncio.create_task(poll_for_submit(client, topics))
        # tasks.add(task)

        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)

# async def poll_for_submit(client, topics):
#     while True:
#         for topic in topics:
#             message = 1
#             print(f'[topic="{topic}"] Publishing message={message}')
#             await client.publish(topic, message, qos=1)
#             await asyncio.sleep(2)

async def process_submit(client, messages):
    async for message in messages:
        if message.topic == "nodeshare/submit":
            msg = message.payload.decode()
            json_data = json.loads(msg)
            node_id = json_data['node_id']
            node_text = json_data['node_text']
            if node_text and node_id:
                print(f'''
    #####################################################

    [  INFO  ]  Submission Received: {json.dumps(json_data)}

    #####################################################
                ''')
                await get_approval(json_data)
                await client.publish("nodeshare/submit/ack", "approved!", qos=1)
            else:
                await client.publish("nodeshare/submit/ack", "Data Error! Requires node_text and node_id", qos=1)
            
            # try:
            #     await get_approval(msg)
            #     await client.publish("nodeshare/submit/ack", "approved!", qos=1)
            #     print("[  INFO ]  Node passed approval test!")
            # except:
            #     await client.publish("nodeshare/submit/ack", "failed submission", qos=1)
            await asyncio.sleep(2)


async def log_messages( messages, template):
    async for message in messages:
        # 🤔 Note that we assume that the message paylod is an
        # UTF8-encoded string (hence the `bytes.decode` call).
        print(template.format(message.payload.decode()))
        

async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def main():
    # Run the advanced_example indefinitely. Reconnect automatically
    # if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await advanced_example()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)


async def get_approval(json_data):    
    print(f"############# Trying to get approval #############")
    node_id = json_data['node_id']
    node_text = json_data['node_text']
    comm = ['C:\Program Files\Blender Foundation\Blender 2.90/blender.exe', '--background', 'ns-test2.blend', '--python', './approval-test.py', '--nodetext', node_text, node_id]
    p = subprocess.run(comm, shell=True)
    await asyncio.sleep(15)


if __name__ == "__main__":
    print('''
    #####################################################
    Starting MQTT Event Loop
    #####################################################

    ''')
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())