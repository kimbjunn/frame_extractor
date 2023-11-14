#Fragmented MP4 ������ �������� �ʴ´�
#�� ������ ����ϱ� ���ؼ��� ffmpeg�� ��ġ�Ǿ� �־�� �ϸ�, ȯ�溯���� ��ϵǾ� �־�� �Ѵ�

import struct
import subprocess

def hvcC(data, ftyp_offsets): # ���Ҵ� ������ �� ������ ���� hvcC �Ķ���� ����

    hvcC_keyword = b'hvcC'

    VPS_extracted = 0 #VPS ���� �� �ӽ� ����, �ʱ�ȭ
    SPS_extracted = 0 #SPS ���� �� �ӽ� ����, �ʱ�ȭ
    PPS_extracted = 0 #PPS ���� �� �ӽ� ����, �ʱ�ȭ

    for idx, start_offset in enumerate(ftyp_offsets[:-1]):
        end_offset = ftyp_offsets[idx + 1] # �˻� ������ ���� ���� mp4 ������ ������
        hvcC_offset = data[start_offset:end_offset].find(b'hvcC')
        print("relative offset : ", hvcC_offset)

        hvcC_offset += start_offset # hvcC�� ��ġ�� ��ü ���Ͽ����� ��ġ�� ��ȯ (����ּ� -> �����ּ�)
        print("absolute offset : ", hvcC_offset)

        if hvcC_offset != -1: # hvcC�� ������ ��
            nal_units_parameters = {
                32: "VPS",
                33: "SPS",
                34: "PPS"
            }
        else:
            print("hvcC not found from range", start_offset, "to", end_offset)
            continue
    
        #hvcC size
        hvcC_size = struct.unpack('>I', data[hvcC_offset-4:hvcC_offset])[0]

        offset = hvcC_offset + 4 #�˻� ������ ����

        length_offset = hvcC_offset 

        parameter = 0 #parameter ���� ī��Ʈ
        VPS_extracted = 0 #VPS ���� �� �ӽ� ����, �ʱ�ȭ
        SPS_extracted = 0 #SPS ���� �� �ӽ� ����, �ʱ�ȭ
        PPS_extracted = 0 #PPS ���� �� �ӽ� ����, �ʱ�ȭ


        while offset < hvcC_offset + hvcC_size + 4: #hvcC �ڽ��� ������ �˻�


            #���� 1����Ʈ�� NALU type�� �˻�

            if parameter >= 3 :
                break

            nal_unit_type = (data[offset] >> 1) & 0x3f
        
            #NALU Type ã��
            if nal_unit_type in nal_units_parameters:
                #NALU�� Length
                length = struct.unpack('>H', data[offset - 2:offset])[0]
                print(nal_units_parameters[nal_unit_type], offset)
                parameter += 1
                if nal_unit_type == 32 and data[offset + 1] == 1:
                    # Extract VPS
                    VPS_extracted = data[offset:offset+length]
                    #VPS.append(VPS_extracted)
                    print(idx, "_video_VPS" "\n")
                    offset = offset + length
                elif nal_unit_type == 33 and data[offset + 1] == 1:
                    # Extract SPS
                    SPS_extracted = data[offset:offset+length]
                    #SPS.append(SPS_extracted)
                    print(idx , "_video_SPS", "\n")
                    offset = offset + length
                elif nal_unit_type == 34 and data[offset + 1] == 1:
                    # Extract PPS
                    PPS_extracted = data[offset:offset+length]
                    #PPS.append(PPS_extracted)
                    print(idx, "_video_PPS", "\n")
                    offset = offset + length
            
            else:
                offset += 1


        with open(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/decoding_header_{idx}', 'ab') as f:#������ ��� �Է�
                f.write(b'\x00\x00\x01' + VPS_extracted)
                f.write(b'\x00\x00\x01' + SPS_extracted)
                f.write(b'\x00\x00\x01' + PPS_extracted)
        
    return 


def ftyp(data):#mp4 ������ �������� ã�Ƽ� �� ������ �������� ��ȯ
    # ���� ���� �����ϴ� mp4 ������ ���� Ȯ�� -> �� ������ ���� �������� ��ȯ
    ftyp_offsets = []
    offset = 0
    start_from_zero = 0
    last_is_end_of_file = len(data)

    while offset + 4 < len(data):
        pos = data[offset:].find(b'ftyp') 
        if pos == -1:
            break
        offset += pos
        ftyp_offsets.append(offset)
        offset += 4

    ftyp_offsets.insert(0, start_from_zero) #ù��° ������ �������� 0���� ����
    ftyp_offsets.append(last_is_end_of_file) #������ ������ ������ ������ ������ ����

    return ftyp_offsets

def stco(data, ftyp_offsets):

    start_from_zero = 0
    first_chunk_offset_list = []

    for idx, start_offset in enumerate(ftyp_offsets[:-1]):
        end_offset = ftyp_offsets[idx + 1]
        stco_offset = data[start_offset:end_offset].find(b'stco')
        if stco_offset == -1:
            stco_offset = data[start_offset:end_offset].find(b'co64')
            
            if stco_offset == -1:
                print("stco not found in range ", start_offset, " to ", end_offset)
                print("Now we find mdat ", start_offset, " to ", end_offset)

                stco_offset = data[start_offset:end_offset].find(b'mdat') #stco�� �������� ���� ��� (overwrite ���� ������) mdat�� ��ġ���� �˻�
                stco_offset += 4
                if stco_offset == -1:
                    print("mdat not found in range ", start_offset, " to ", end_offset)
                    continue
                stco_offset += start_offset
                first_chunk_offset_list.append(stco_offset)
                continue        

            stco_offset += start_offset #���� �ּҷ� ����
            first_chunk_offset = struct.unpack('>Q', data[stco_offset + 12:stco_offset + 20])[0]
            print("first_chunk_offset : ", first_chunk_offset)

            first_chunk_offset = start_offset + first_chunk_offset #���� �ּҷ� ����
            first_chunk_offset_list.append(first_chunk_offset)

            continue


        else:
            stco_offset += start_offset #���� �ּҷ� ����
            
            first_chunk_offset = struct.unpack('>I', data[stco_offset + 12:stco_offset + 16])[0]
            print("first_chunk_offset : ", first_chunk_offset)
            
            first_chunk_offset = start_offset + first_chunk_offset #���� �ּҷ� ����
            first_chunk_offset_list.append(first_chunk_offset)
             
            #���Ҵ� ������ ���ۺ��� ftyp����Ʈ�� 0�� �ε��� ���̿��� �ݵ�� ���� ������ �������� ����

    first_chunk_offset_list.insert(0, start_from_zero)
    return first_chunk_offset_list


def frame(data, ftyp_offsets, first_chunk_offset_list):


    for idx, start_offset in enumerate(ftyp_offsets[:-1]):
        for_extract_first_I_frame = 0
        end_offset = ftyp_offsets[idx + 1]
        mdat_offset = data[start_offset:end_offset].find(b'mdat')

        mdat_offset += start_offset

        if mdat_offset == -1:
            print("mdat not found in range ", start_offset, " to ", end_offset)
            continue

        if for_extract_first_I_frame == 0:
            frame_parameters = {
                19: "I",
                20: "I",
                14 : "I", #Galaxy S21's Video
            }

        mdat_size = struct.unpack('>I', data[mdat_offset - 4:mdat_offset])[0]
        if mdat_size == 1:
            mdat_size = struct.unpack('>I', data[mdat_offset + 8:mdat_offset + 12])[0]

            if mdat_size <= 1:
                print("mdat_size error")
                continue

        offset = first_chunk_offset_list[idx]

        while offset < mdat_offset + mdat_size and offset < end_offset:
            if for_extract_first_I_frame == 1:
                frame_parameters = {
                19: "I",
                20: "I",
                14 : "I", #Galaxy S21's Video
                0: "P/B_frame(Trail_N)",
                1: "P/B_frame(Trail_R)"
                }

            nal_unit_type = (data[offset] >> 1) & 0x3f

            if nal_unit_type in frame_parameters:
                length = struct.unpack('>I', data[offset - 4:offset])[0]
                if offset + length < mdat_offset + mdat_size and length > 0:#������ ������� mdat �ڽ��� ũ�⸦ ���� �ʾƾ���

                    if length < mdat_size and length > 0 and data[offset - 4] == 0:
                        # I-frames 
                        if nal_unit_type in [14, 19, 20] and data[offset + 1] == 1:
                            if offset >= mdat_offset + mdat_size:
                                break
                            I_extracted = data[offset:offset + length]
                            with open(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame_{idx}', 'ab') as f:#��� �Է� ���ϸ��� ����X
                                f.write(b'\x00\x00\x01' + I_extracted)
                            print(idx, "_video_I : ", "\n")
                            offset += length

                            for_extract_first_I_frame = 1

                            continue  # ����Ʈ �˻� ��� ����

                        # P-frames
                        elif nal_unit_type in [0, 1] and data[offset + 1] == 1:
                            if offset >= mdat_offset + mdat_size:
                                break
                            P_extracted = data[offset:offset + length]
                            with open(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame_{idx}', 'ab') as f:#��� �Է� ���ϸ��� ����X
                                f.write(b'\x00\x00\x01' + P_extracted)
                            print(idx, "_video_P : ", "\n")
                            offset += length


                            continue  # ����Ʈ �˻� ��� ����
                

                        else:
                            offset += 1
                            continue
                
                    else:
                        offset += 1
                        continue
                

                else:
                    offset += 1  # ����Ʈ �̵�

            else:
                offset += 1
                continue

    return


def merge_files(file1_path, file2_path, output_file_path):
    # ù ��° ����
    with open(file1_path, 'rb') as file1:
        data1 = file1.read()
    
    # �� ��° ����
    with open(file2_path, 'rb') as file2:
        data2 = file2.read()
    
    # �� ������ ���� �����մϴ�.
    merged_data = data1 + data2
    
    # ���ο� ���Ͽ� ����.
    with open(output_file_path, 'wb') as output_file:
        output_file.write(merged_data)
    
    print(f"merge decoding header and frame data. output save on '{output_file_path}'")


def extract_frame_to_jpg(file_path, output_path):
    try:
        # ffplay ��ɾ ����.
        ffmpeg_command = ['ffmpeg','-i', file_path, f'{output_path}%d.jpg']

        # ������ ���� ��ɾ� ����.
        subprocess.run(ffmpeg_command, check=True)

    except subprocess.CalledProcessError:
        print("ffmpeg error")
    except Exception as e:
        print(f"error: {str(e)}")



if __name__ == "__main__":
    with open('C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/over_50_bun', 'rb') as f:
        data = f.read()

    ftyp_offset = ftyp(data) #ftyp�� offset�� ����
    print(ftyp_offset)


    hvcC(data, ftyp_offset) #hvcC �Ķ���� ����
    first_chunk_offset = stco(data, ftyp_offset) #stco �Ķ���� ����
    frame(data, ftyp_offset, first_chunk_offset) #I,P frame ����

    for index in range(1, len(ftyp_offset) - 1):
        merge_files(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/decoding_header_{index}', f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame_{index}', f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/merge_{index}')#��� �Է� ���ϸ��� ����X
        print(f"complete video_{index}")
        extract_frame_to_jpg(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/merge_{index}', f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame/{index}vid_frame_')#��� �Է� ���ϸ��� ����X
        print(f"extract video_{index}")

    
