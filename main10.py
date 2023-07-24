from tkinter import *
from PIL import ImageTk, Image
from speedtest import Speedtest
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket
import time


class SpeedTestData:
    def __init__(self):
        self.data = []

    def add_data(self, download, upload, latency, packet_loss, dns_time, jitter, bandwidth, throughput):
        self.data.append({
            'download': download,
            'upload': upload,
            'latency': latency,
            'packet_loss': packet_loss,
            'dns_time': dns_time,
            'jitter': jitter,
            'bandwidth': bandwidth,
            'throughput': throughput
        })

    def get_data(self):
        return self.data


speed_test_data = SpeedTestData()


def get_speedtest():
    s = Speedtest()
    network_name = s.get_best_server()["sponsor"]
    download = s.download() / 10 ** 6
    upload = s.upload() / 10 ** 6
    latency = s.results.ping
    results = s.results.dict()

    # Calculate packet loss if available
    packet_loss = results.get("packet_loss")
    if packet_loss is not None:
        packet_sent = results.get("packet_sent")
        packet_loss_value = round((packet_loss / packet_sent) * 100, 2)
    else:
        packet_loss_value = 0

    download_speed = round(download, 2)
    upload_speed = round(upload, 2)
    latency_value = round(latency, 2)

    # DNS resolution time and jitter calculation
    dns_start_time = time.time()
    socket.gethostbyname("www.nitsri.ac.in")  
    dns_end_time = time.time()
    dns_time = round((dns_end_time - dns_start_time) * 1000, 2)

    # Jitter calculation
    last_latency = speed_test_data.get_data()[-1]['latency'] if speed_test_data.get_data() else 0
    jitter = abs(last_latency - latency_value)

    # Bandwidth and throughput calculation
    bandwidth = results["client"]["isp"]
    throughput = results["download"] / results["ping"] / 10 ** 6

    down_lab.config(text='Download Speed: ' + str(download_speed) + " Mbps")
    upload_lab.config(text='Upload Speed: ' + str(upload_speed) + " Mbps")
    network_lab.config(text='Network: ' + network_name)
    latency_lab.config(text='Latency: ' + str(latency_value) + " ms")
    packet_loss_lab.config(text='Packet Loss: ' + str(packet_loss_value) + " %")
    dns_time_lab.config(text='DNS Resolution Time: ' + str(dns_time) + " ms")
    jitter_lab.config(text='Jitter: ' + str(jitter) + " ms")
    bandwidth_lab.config(text='Bandwidth: ' + bandwidth)
    throughput_lab.config(text='Throughput: {:.2f} Mbps'.format(throughput))

    # Calculate network health
    health_status = get_health_status(download_speed, upload_speed, latency, packet_loss_value, dns_time)
    health_lab.config(text='Network Health: ' + health_status)

    # Update graphs
    update_graphs(download_speed, upload_speed, latency_value, throughput, dns_time, jitter)

    # Save the current speed test data
    speed_test_data.add_data(download_speed, upload_speed, latency_value, packet_loss_value, dns_time, jitter, bandwidth, throughput)


def get_health_status(download_speed, upload_speed, latency, packet_loss, dns_time_threshold):
    # Define thresholds for different metrics
    download_threshold = 50  # Mbps
    upload_threshold = 10  # Mbps
    latency_threshold = 50  # ms
    packet_loss_threshold = 1  # %
    dns_time_threshold = 20  #ms

    # Check each metric against the respective threshold
    if download_speed >= download_threshold and upload_speed >= upload_threshold and latency <= latency_threshold and packet_loss <= packet_loss_threshold:
        return "Good"
    else:
        return "Poor"


def update_graphs(download_speed, upload_speed, latency, throughput, dns_time, jitter):
    # Get the historical data
    data = speed_test_data.get_data()

    # Extract the individual metrics from the historical data
    download_values = [entry['download'] for entry in data]
    upload_values = [entry['upload'] for entry in data]
    latency_values = [entry['latency'] for entry in data]
    throughput_values = [entry['throughput'] for entry in data]
    dns_time_values = [entry['dns_time'] for entry in data]
    jitter_values = [entry['jitter'] for entry in data]

    # Add the latest speed test results to the data
    download_values.append(download_speed)
    upload_values.append(upload_speed)
    latency_values.append(latency)
    throughput_values.append(throughput)
    dns_time_values.append(dns_time)
    jitter_values.append(jitter)

    # Generate x-axis labels
    num_data_points = len(download_values)
    labels = [f'Data {i+1}' for i in range(num_data_points)]

    # Update download speed graph
    ax1.clear()
    ax1.bar(labels, download_values, color='b', align='center')
    ax1.set_ylabel('Speed (Mbps)', fontweight='bold')
    ax1.set_title('Download Speed', fontweight='bold')
    ax1.tick_params(axis='both', which='both', length=0)

    # Update upload speed graph
    ax2.clear()
    ax2.bar(labels, upload_values, color='r', align='center')
    ax2.set_ylabel('Speed (Mbps)', fontweight='bold')
    ax2.set_title('Upload Speed', fontweight='bold')
    ax2.tick_params(axis='both', which='both', length=0)

    # Update latency graph
    ax3.clear()
    ax3.bar(labels, latency_values, color='g', align='center')
    ax3.set_ylabel('Latency (ms)', fontweight='bold')
    ax3.set_title('Latency', fontweight='bold')
    ax3.tick_params(axis='both', which='both', length=0)

    # Update throughput graph
    ax4.clear()
    ax4.bar(labels, throughput_values, color='m', align='center')
    ax4.set_ylabel('Throughput (Mbps)', fontweight='bold')
    ax4.set_title('Throughput', fontweight='bold')
    ax4.tick_params(axis='both', which='both', length=0)

    # Update DNS resolution time graph
    ax5.clear()
    ax5.bar(labels, dns_time_values, color='y', align='center')
    ax5.set_ylabel('Time (ms)', fontweight='bold')
    ax5.set_title('DNS Resolution Time', fontweight='bold')
    ax5.tick_params(axis='both', which='both', length=0)

    # Update jitter graph
    ax6.clear()
    ax6.bar(labels, jitter_values, color='c', align='center')
    ax6.set_ylabel('Jitter (ms)', fontweight='bold')
    ax6.set_title('Jitter', fontweight='bold')
    ax6.tick_params(axis='both', which='both', length=0)

    # Redraw the figure
    fig.canvas.draw()

def save_data():
    data = speed_test_data.get_data()
    if not data:
        return

    with open('speedtest_data.csv', 'w') as file:
        file.write('Download Speed (Mbps),Upload Speed (Mbps),Latency (ms),Packet Loss (%),DNS Resolution Time (ms),Jitter (ms), Throughput (Mbps)\n')
        for entry in data:
            file.write(
                f'{entry["download"]},{entry["upload"]},{entry["latency"]},{entry["packet_loss"]},{entry["dns_time"]},{entry["jitter"]},{entry["throughput"]}\n'
            )


def show_historical_data():
    data = speed_test_data.get_data()
    if not data:
        return

    top = Toplevel(root)
    top.title("Historical Data")

    # Create a text widget to display the data
    text_widget = Text(top, width=40, height=10)
    text_widget.pack(padx=10, pady=10)

    # Insert the data into the text widget
    text_widget.insert(END, 'Download Speed (Mbps), Upload Speed (Mbps), Latency (ms), Packet Loss (%), DNS Resolution Time (ms), Jitter (ms), Bandwidth, Througput \n')
    for entry in data:
        text_widget.insert(END,
                           f'{entry["download"]}, {entry["upload"]}, {entry["latency"]}, {entry["packet_loss"]}, {entry["dns_time"]}, {entry["jitter"]}, {entry["bandwidth"]}, {entry["throughput"]}\n')

    # Make the text widget read-only
    text_widget.configure(state='disabled')


# Create the main Tkinter window
root = Tk()
root.title("Speed Test Application")

# Create a canvas to display the graphs
fig = plt.figure(figsize=(8, 6), tight_layout=True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)

# Create axes for the graphs
ax1 = fig.add_subplot(231)
ax2 = fig.add_subplot(232)
ax3 = fig.add_subplot(233)
ax4 = fig.add_subplot(234)
ax5 = fig.add_subplot(235)
ax6 = fig.add_subplot(236)

# Manually call the update_graphs function to initialize the graphs with default titles
update_graphs(0, 0, 0, 0, 0, 0)

# Create labels to display the speed test results
down_lab = Label(root, text="Download Speed: - Mbps")
down_lab.grid(row=1, column=0, sticky='W')

upload_lab = Label(root, text="Upload Speed: - Mbps")
upload_lab.grid(row=2, column=0, sticky='W')

network_lab = Label(root, text="Network: -")
network_lab.grid(row=1, column=1, sticky='W')

latency_lab = Label(root, text="Latency: - ms")
latency_lab.grid(row=2, column=1, sticky='W')

packet_loss_lab = Label(root, text="Packet Loss: - %")
packet_loss_lab.grid(row=3, column=0, sticky='W')

dns_time_lab = Label(root, text="DNS Resolution Time: - ms")
dns_time_lab.grid(row=4, column=0, sticky='W')

jitter_lab = Label(root, text="Jitter: - ms")
jitter_lab.grid(row=4, column=1, sticky='W')

bandwidth_lab = Label(root, text="Bandwidth: ")
bandwidth_lab.grid(row=5, column=0, sticky='W')

throughput_lab = Label(root, text="Throughput: ")
throughput_lab.grid(row=5, column=1, sticky='W')

health_lab = Label(root, text="Network Health: -")
health_lab.grid(row=3, column=1, sticky='W')

# Create buttons to trigger actions
speed_test_btn = Button(root, text="Run Speed Test", command=get_speedtest)
speed_test_btn.grid(row=6, column=0, pady=10)

save_btn = Button(root, text="Save Data", command=save_data)
save_btn.grid(row=6, column=1, pady=10)

show_data_btn = Button(root, text="Show Historical Data", command=show_historical_data)
show_data_btn.grid(row=7, column=0, columnspan=2, pady=10)

# Start the Tkinter event loop
root.mainloop()
