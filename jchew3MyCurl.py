# Python program to request and download web objects from any public web
# server. The functionality of this program is similar to Curl. The user
# of the application enters a URL on the command line, which in turn 
# causes an HTTP GET request to be issued for the object. Upon successful
# retrieval the object is written to a file. If an error or redirection
# is returned from the web server, the HTTP response message is
# interpreted and displayed in the terminal.

import sys
import argparse
import re
import csv
import socket
#from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('fullURL')
parser.add_argument('opthostname', nargs='?', default='none')
args = parser.parse_args()

urlparts = args.fullURL.split('://')
scheme = urlparts[0]
# hostportpath contains the domain name/IP Addr, and (optional) port and path
hostportpath = urlparts[1]

# Check if protocol is HTTPS, then print an error
if scheme == 'https':
    sys.exit('HTTPS is not supported.')
if scheme == 'http':
    pass
else:
    sys.exit('Invalid URL input.')


#print(hostportpath)

# Parse host, port, and path fields from url
host = re.match(r'(.*?)(:|/|$)', hostportpath) # Match until first occurrence of ':', '/', or end of string
host = host.group(1) # group(1) returns first parenthesized subgroup as string

port = re.search(r':(\d*)', hostportpath) # Match digits following colon
if port is None:
    port = 80
else:
    port = int(port.group(1))

# Match characters following dash, but preceding ':', whitespace, '\n', or end of string
path = re.search(r'/(.*)(:|\s|\n|$)', hostportpath) 
if path is None:
    path = ""
else:
    path = path.group(1)

# print(host)
# print(port)
# print(path)


# Open html file and csv file
htmlFile = open("HTTPoutput.html", "w", encoding="utf-8")  # 'w' = overwrite file
csvFile = open("Log.csv", "a", encoding="utf-8", newline='') # 'a' = append to file
# Create csv writer
writer = csv.writer(csvFile)


# Create client TCP socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.settimeout(5)
# Initiate a TCP connection between client and server
try:
    clientSocket.connect((host, port))  # Connect to server using server hostname and portnum
except socket.gaierror as ge:  # Handles hosts that don't exist/can't be resolved
    print("socket.gaierror")
    # Close files
    htmlFile.close()
    csvFile.close()
    # Close client socket
    clientSocket.close()
    sys.exit("Socket exception: %s" % ge)
except socket.timeout as te:  # Handles socket indefinitely hangs (port not 80)
    print("socket.timeout")
    # Close files
    htmlFile.close()
    csvFile.close()
    # Close client socket
    clientSocket.close()
    sys.exit("Socket exception: %s" % te)


# Create HTTP GET request
sentence = "GET /" + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
# Send GET request through socket and into TCP connection
# encode() turns the sentence string into bytes
try:
    clientSocket.send(sentence.encode())
    pass
except socket.error as e:
    print("socket.error")
    # Close files
    htmlFile.close()
    csvFile.close()
    # Close client socket
    clientSocket.close()
    sys.exit("Error sending through socket: %s" % e)



# Check if host is an IP address; if so, hostname must be provided as second arg
if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host) is not None:
    if len(sys.argv) != 3:
        # Close files
        htmlFile.close()
        csvFile.close()
        # Close client socket
        clientSocket.close()
        sys.exit('Domain name must be given for Host header as a second argument.')
    else:
        # Change host variable to contain domain name 
        ip_addr = host
        host = args.opthostname


# Receive response from server; buffer size for recv is 2048
try:
    serverResponse = clientSocket.recv(2048)
    pass
except ConnectionError as err: # Handles ConnectionRefusedError or ConnectionResetError
    # Close files
    htmlFile.close()
    csvFile.close()
    # Close client socket
    clientSocket.close()
    sys.exit(err)

bytes_recv = len(serverResponse)
#print(bytes_recv)

# print(serverResponse.decode("ISO-8859-1"))
# print('*************************************\n')

# Check for empty reply from server; 0 bytes returned in HTTP response
if bytes_recv == 0:
    # Write to log.csv
    csvFile.write("\n")
    writer.writerow([   "Unsuccessful",                    # Status of retrieval
                        "",                                # Server status code
                        args.fullURL,                      # Requested URL
                        host,                              # Hostname
                        clientSocket.getsockname()[0],     # Source IP (Router)
                        socket.gethostbyname(host),        # Destination IP
                        clientSocket.getsockname()[1],     # Source port (Router)
                        port,                              # Destination port
                        "curl: (52) Empty reply from server"   # Server Response line
                    ])
    # Close files
    htmlFile.close()
    csvFile.close()
    # Close client socket
    clientSocket.close()
    sys.exit('Empty reply from server.')


# ISO-8859-1 is an encoding containing Latin characters; this will be the default
encoding = "ISO-8859-1" 
responseStatusHeader = serverResponse.decode(encoding).split('\r\n\r\n', 1)[0]

statusLine = re.search(r'HTTP/1.1.*\r\n', responseStatusHeader)
statusLine = statusLine.group(0)  # group(0) returns the entire match as string
# print(statusLine)

statusCode = re.search(r'\s(\d*)\s', statusLine)
statusCode = statusCode.group(1)  # group(1) returns first parenthesized subgroup as string
# print(statusCode)

# Check if requested object is returned with chunk encoding
if 'Transfer-Encoding: chunked' in responseStatusHeader:
    # Write to log.csv
    csvFile.write("\n")
    writer.writerow([   "Unsuccessful",                    # Status of retrieval
                        statusCode,                        # Server status code
                        args.fullURL,                      # Requested URL
                        host,                              # Hostname
                        clientSocket.getsockname()[0],     # Source IP (Router)
                        socket.gethostbyname(host),        # Destination IP
                        clientSocket.getsockname()[1],     # Source port (Router)
                        port,                              # Destination port
                        statusLine                         # Server Response line
                    ])
    print("Unsuccessful\n" + args.fullURL + "\n" + statusLine)
    # Close files
    htmlFile.close()
    csvFile.close()
    # Close client socket
    clientSocket.close()
    sys.exit('Chunk encoding is not supported.')

# Status code is 200, object was not returned with chunk encoding
# Requested obejct was returned in the Response
if int(statusCode) == 200:
    # Append to Log.csv
    csvFile.write("\n")
    writer.writerow([   'Successful',                      # Status of retrieval
                        statusCode,                        # Server status code
                        args.fullURL,                      # Requested URL
                        host,                              # Hostname
                        clientSocket.getsockname()[0],     # Source IP (Router)
                        socket.gethostbyname(host),        # Destination IP
                        clientSocket.getsockname()[1],     # Source port (Router)
                        port,                              # Destination port
                        statusLine                         # Server Response line
                    ])
    # Print to terminal with "Success" followed by requested URL and status line
    print("Success\n" + args.fullURL + "\n" + statusLine)

else: # If status code is not 200; Requested object was not returned in response
    # Write to log.csv
    csvFile.write("\n")
    writer.writerow([   "Unsuccessful",                    # Status of retrieval
                        statusCode,                        # Server status code
                        args.fullURL,                      # Requested URL
                        host,                              # Hostname
                        clientSocket.getsockname()[0],     # Source IP (Router)
                        socket.gethostbyname(host),        # Destination IP
                        clientSocket.getsockname()[1],     # Source port (Router)
                        port,                              # Destination port
                        statusLine                         # Server Response line
                    ])
    print("Unsuccessful\n" + args.fullURL + "\n" + statusLine)

# Choose encoding type, depending on Content-Type header field, for writing web object to HTTPoutput.html
# This ensures that the encoding matches with curl's output
charset = re.search(r'Content-Type:(.*)', responseStatusHeader)
charset = charset.group(1) # group(1) returns first parenthesized subgroup as string
if "charset=" in charset:
    encoding = charset.split('charset=', 1)[1]
else:
    encoding = "ISO-8859-1"  #ISO-8859-1

# Write response body to the file
respBody = serverResponse.decode(encoding).split('\r\n\r\n', 1)[1]
htmlFile.write(respBody)

# Find Content-Length value in order to read all bytes in response body
dataLength = re.search(r'Content-Length:(.*)', responseStatusHeader)
dataLength = int(dataLength.group(1)) # group(1) returns first parenthesized subgroup as string

# Length of entire HTTP response  ( +4 to account for '\r\n\r\n' missing in responseStatusHeader)
responseLength = dataLength + len(responseStatusHeader) + 4

while bytes_recv < responseLength:
    serverResponse = clientSocket.recv(min(responseLength - bytes_recv, 2048))
    
    # print(serverResponse.decode("ISO-8859-1"))
    # print('*************************************\n')
    
    if serverResponse == '':  # No bytes received
        break
    # Write to html file
    htmlFile.write(serverResponse.decode(encoding))
    bytes_recv = bytes_recv + len(serverResponse)
    #print(bytes_recv)





# Close files
htmlFile.close()
csvFile.close()

# Close client socket
clientSocket.close()
