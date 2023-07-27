# Python program to request and download web objects from any public web
# server. The functionality of this program is similar to Curl. The user
# of the application enters a URL on the command line, which in turn 
# causes an HTTP GET request to be issued for the object. Upon successful
# retrieval the object is written to a file. If an error or redirection
# is returned from the web server, the HTTP response message is
# interpreted and displayed in the terminal.

from dataclasses import dataclass
from http import server
import sys
import argparse
import re
import socket
from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('fullURL')
parser.add_argument('opthostname', nargs='?', default='none')
args = parser.parse_args()

urlparts = args.fullURL.split('://')
scheme = urlparts[0]
hostportpath = urlparts[1]

# Check if protocol is HTTPS, then print an error
if scheme == 'https':
    sys.exit('HTTPS is not supported.')
if scheme == 'http':
    pass
else:
    sys.exit('Invalid URL input.')


print(hostportpath)
# hostportpath contains the domain name/IP Addr, and (optional) port and path
if ':' in hostportpath:         # Port number is given
    host, portpath = hostportpath.split(':')
    if '/' in portpath:         # Path is given
        port, path = portpath.split('/', 1)
    else:
        port = portpath
        path = ""
    port = int(port)
else:                           # No port number given
    port = 80                   # Default port is port 80
    if '/' in hostportpath:     # Path is given
        host, path = hostportpath.split('/', 1)
    else:
        host = hostportpath
        path = ""

print(host)
print(port)
print(path)

# Check if host is an IP address; if so, hostname must be provided as second arg
if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host) is not None:
    if len(sys.argv) != 3:
        sys.exit('Domain name must be given for Host header as a second argument.')
    else:
        # Change host variable to contain domain name 
        ip_addr = host
        host = args.opthostname


# Create client TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)
# Initiate a TCP connection between client and server
clientSocket.connect((host, port))  # Connect to server using server hostname and portnum

# Create HTTP GET request
sentence = "GET /" + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
# Send GET request through socket and into TCP connection
# encode() turns the sentence string into bytes
clientSocket.send(sentence.encode())


# Response received from server; buffer size for recv is 2048
serverResponse = clientSocket.recv(2048)
bytes_recv = len(serverResponse)
print(bytes_recv)

# Write response body to html file
respBody = serverResponse.decode("ISO-8859-1").split('\r\n\r\n', 1)[1]
htmlFile = open("HTTPoutput.html", "a")  # 'a' = append to file
htmlFile.write(respBody)

# Find Content-Length value in order to read all bytes in response body
dataLength = re.search(r'Content-Length:(.*)\r\n', serverResponse.decode("ISO-8859-1"))
dataLength = int(dataLength.group(1)) # group(1) returns a string of matched text

responseStatusHeader = serverResponse.decode("ISO-8859-1").split('\r\n\r\n', 1)[0]
print(len(responseStatusHeader)+4)
statusHeaderLen = len(responseStatusHeader) + 4  # 4 bytes to account for '\r\n\r\n' 
bytes_left = (dataLength + statusHeaderLen) - bytes_recv
while bytes_left > 0:
    serverResponse = clientSocket.recv(2048)
    htmlFile.write(serverResponse.decode("ISO-8859-1"))
    if bytes_left > 2048:
        bytes_left = bytes_left - 2048
    else:
        bytes_left



# WRITE TO LOG.SV HERE!!!!!!!

print(serverResponse.decode("ISO-8859-1"))
print('*************************************\n')
# Check if requested object is returned with chunk encoding
if 'Transfer-Encoding: chunked' in responseStatusHeader:
    sys.exit('Chunk encoding is not supported.')



#webObject = serverResponse.split('\r\n\r\n', 1)[1]

# Store body of HTTP response into webObject variable
# ISO-8859-1 is an encoding containing Latin characters
# webObject = serverResponse.decode("ISO-8859-1").split('\r\n\r\n', 1)[1]
#print(webObject)


# Open and write to html file the 
# htmlFile = open("HTTPoutput.html", "w")  # 'a' = append to file
# htmlFile.write(webObject)




# Close files
htmlFile.close()

# Close client socket
clientSocket.close()
