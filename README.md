# piTorrent
A simple BitTorrent client written in Python

## Prerequisites

* qBitTorrent

qBitTorrent is needed to create a private tracker that runs on your local machine itself. Other torrent clients
can also be used (Transmission doesn't have this feature). To install qBitTorrent, run:

``` sudo apt-get install qbittorrent ```

After the installation is done, go to qBitTorrent -> Tools -> Options -> Advanced. Set the "Embedded tracker port"
to 9000 and make sure "Enable embedded tracker" box is checked.

## Running the client

Download the source code:

``` git clone https://github.com/rithvikp1998/piTorrent ```

To run the client, cd into the source code directory and run the following line:

``` python3 piTorrent.py --metafile utils/multi_file_set.torrent --dest ~/piTorrent/trash ```

You can change the source metafile and destination options according to your needs. 

To create multiple peers simultaneously, I currently use a virtual machince. However, the code can be modified to
support multiple peers running with the same ip, but different ports on the same machine.

## Disclaimer

Please note that this is a personal project and not a product. This project is intended to be used for fun and if
needed, educational purposes. Nevertheless, the code comes with GPL v3, so feel free to use it the way you like :)
