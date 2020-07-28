# # SDO Parser Tests
# import os
#
# from src.parser.eds import load_eds_file
# from src.parser.sdo import *
#
#
# def test_sdo():
#     eds_data = load_eds_file(os.getcwd() + "/data/test.eds")
#     parser = SDOParser(eds_data)
#
#     # Initiate Client Download Message
#     client_initiate_message = b'\x21\x10\x18\x00\x00\x00\x00\x0C'
#     print(parser.parse_sdo_download(0x12, client_initiate_message))
#     server_initiate_response = b'\x60\x10\x18\x00\x00\x00\x00\x00'
#     print(parser.parse_sdo_download(0x12, server_initiate_response))
#     client_download_segment = b'\x11\x00\x00\x00\x00\x00\x00\x0A'
#     print(parser.parse_sdo_download(0x12, client_download_segment))
#     server_download_response = b'\x20\x00\x00\x00\x00\x00\x00\x00'
#     print(parser.parse_sdo_download(0x12, server_download_response))
#
#     # SDO Parser test
#     initiate_sdo = SDODownloadInitiate(client_initiate_message)
#     assert initiate_sdo.isExpedited is False
#     assert initiate_sdo.isClient is True
#     assert initiate_sdo.sizeIndicator is True
#     assert initiate_sdo.index == b'\x10\x18\x00'
#     assert initiate_sdo.data == b'\x00\x00\x00\x0C'
