import can

# Create two virtual CAN nodes
sender = can.Bus(
    interface="virtual",
    channel="can0"
)

receiver = can.Bus(
    interface="virtual",
    channel="can0"
)

# Create a CAN message
message = can.Message(
    arbitration_id=0x101,
    data=[0x12, 0x34, 0x56, 0x78],
    is_extended_id=False
)

# Display the message before sending
print("Message created:")
print(message)

# Send the CAN message
sender.send(message)

print("\nMessage sent successfully!")

# Receive the message
received_message = receiver.recv(timeout=2)

if received_message is not None:

    print("\nMessage received!")

    print("CAN ID :", hex(received_message.arbitration_id))
    print("DLC    :", received_message.dlc)
    print("DATA   :", received_message.data.hex(" "))

else:
    print("\nNo message received.")

# Shut down the virtual CAN interfaces
sender.shutdown()
receiver.shutdown()