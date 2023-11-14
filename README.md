# Frame Extractor from unallocated space in FAT32 File system

To use this tool, ffmpeg must be installed, and environmental variables need to be registered.
The file "over_[overwrite ratio]" is an experiment file.

Files with "over_[ratio]_bun" suffix are experiment files where portions of the sample video "Big Buck Bunny" are overwritten.
Files without "bun" are experiment files where "h_265_phone" video is overwritten.

To simulate an environment similar to unallocated space on a typical storage device, the experiment files include a fragmented experiment file and an overwritten experiment file.

Make sure to correctly enter the paths of the analysis file, the destination path, and the location of the target file for merging in the code.

For the "h_265_phone" overwrite experiment, the decoding header, including the hvcC box itself, is overwritten.
During the experiment, comment out the hvcC function and the merge and jpg-to-extract functions to extract the encoded frame data.
Combine this with the decoding header of a video captured under the same conditions on the same device.
Therefore, it is possible to decode using a decoder.

Make sure to use the decoding header included in the "phone_decoding_header" file and combine it to extract frames using a decoder.

You can download the test files on the next link

### The test is conducted by these files
raw video : https://drive.google.com/file/d/1EJoOoSgQCLQpmHvjJnsXBFhADUP7Cvtz/view?usp=sharing
over_50_bun : https://drive.google.com/file/d/113SpCN5FW3PoJHnSwq7_9KesIRaKQJvn/view?usp=sharing
