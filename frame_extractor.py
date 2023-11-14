#Fragmented MP4 파일은 지원하지 않는다
#본 도구를 사용하기 위해서는 ffmpeg가 설치되어 있어야 하며, 환경변수에 등록되어 있어야 한다

import struct
import subprocess

def hvcC(data, ftyp_offsets): # 비할당 영역의 각 동영상에 대한 hvcC 파라미터 추출

    hvcC_keyword = b'hvcC'

    VPS_extracted = 0 #VPS 추출 값 임시 저장, 초기화
    SPS_extracted = 0 #SPS 추출 값 임시 저장, 초기화
    PPS_extracted = 0 #PPS 추출 값 임시 저장, 초기화

    for idx, start_offset in enumerate(ftyp_offsets[:-1]):
        end_offset = ftyp_offsets[idx + 1] # 검색 범위의 끝은 다음 mp4 파일의 시작점
        hvcC_offset = data[start_offset:end_offset].find(b'hvcC')
        print("relative offset : ", hvcC_offset)

        hvcC_offset += start_offset # hvcC의 위치를 전체 파일에서의 위치로 변환 (상대주소 -> 절대주소)
        print("absolute offset : ", hvcC_offset)

        if hvcC_offset != -1: # hvcC가 존재할 때
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

        offset = hvcC_offset + 4 #검사 시작점 설정

        length_offset = hvcC_offset 

        parameter = 0 #parameter 개수 카운트
        VPS_extracted = 0 #VPS 추출 값 임시 저장, 초기화
        SPS_extracted = 0 #SPS 추출 값 임시 저장, 초기화
        PPS_extracted = 0 #PPS 추출 값 임시 저장, 초기화


        while offset < hvcC_offset + hvcC_size + 4: #hvcC 박스의 끝까지 검사


            #다음 1바이트의 NALU type을 검사

            if parameter >= 3 :
                break

            nal_unit_type = (data[offset] >> 1) & 0x3f
        
            #NALU Type 찾기
            if nal_unit_type in nal_units_parameters:
                #NALU의 Length
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


        with open(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/decoding_header_{idx}', 'ab') as f:#저장할 경로 입력
                f.write(b'\x00\x00\x01' + VPS_extracted)
                f.write(b'\x00\x00\x01' + SPS_extracted)
                f.write(b'\x00\x00\x01' + PPS_extracted)
        
    return 


def ftyp(data):#mp4 파일의 시작점을 찾아서 각 영상의 시작점을 반환
    # 공간 내에 존재하는 mp4 영상의 개수 확인 -> 각 영상의 시작 오프셋을 반환
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

    ftyp_offsets.insert(0, start_from_zero) #첫번째 영상의 시작점을 0으로 설정
    ftyp_offsets.append(last_is_end_of_file) #마지막 영상의 끝점을 파일의 끝으로 설정

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

                stco_offset = data[start_offset:end_offset].find(b'mdat') #stco가 존재하지 않을 경우 (overwrite 등의 이유로) mdat의 위치부터 검색
                stco_offset += 4
                if stco_offset == -1:
                    print("mdat not found in range ", start_offset, " to ", end_offset)
                    continue
                stco_offset += start_offset
                first_chunk_offset_list.append(stco_offset)
                continue        

            stco_offset += start_offset #절대 주소로 변경
            first_chunk_offset = struct.unpack('>Q', data[stco_offset + 12:stco_offset + 20])[0]
            print("first_chunk_offset : ", first_chunk_offset)

            first_chunk_offset = start_offset + first_chunk_offset #절대 주소로 변경
            first_chunk_offset_list.append(first_chunk_offset)

            continue


        else:
            stco_offset += start_offset #절대 주소로 변경
            
            first_chunk_offset = struct.unpack('>I', data[stco_offset + 12:stco_offset + 16])[0]
            print("first_chunk_offset : ", first_chunk_offset)
            
            first_chunk_offset = start_offset + first_chunk_offset #절대 주소로 변경
            first_chunk_offset_list.append(first_chunk_offset)
             
            #비할당 영역의 시작부터 ftyp리스트의 0번 인덱스 사이에는 반드시 비디오 파일이 존재하지 않음

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
                if offset + length < mdat_offset + mdat_size and length > 0:#프레임 사이즈는 mdat 박스의 크기를 넘지 않아야함

                    if length < mdat_size and length > 0 and data[offset - 4] == 0:
                        # I-frames 
                        if nal_unit_type in [14, 19, 20] and data[offset + 1] == 1:
                            if offset >= mdat_offset + mdat_size:
                                break
                            I_extracted = data[offset:offset + length]
                            with open(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame_{idx}', 'ab') as f:#경로 입력 파일명은 변경X
                                f.write(b'\x00\x00\x01' + I_extracted)
                            print(idx, "_video_I : ", "\n")
                            offset += length

                            for_extract_first_I_frame = 1

                            continue  # 바이트 검사 계속 진행

                        # P-frames
                        elif nal_unit_type in [0, 1] and data[offset + 1] == 1:
                            if offset >= mdat_offset + mdat_size:
                                break
                            P_extracted = data[offset:offset + length]
                            with open(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame_{idx}', 'ab') as f:#경로 입력 파일명은 변경X
                                f.write(b'\x00\x00\x01' + P_extracted)
                            print(idx, "_video_P : ", "\n")
                            offset += length


                            continue  # 바이트 검사 계속 진행
                

                        else:
                            offset += 1
                            continue
                
                    else:
                        offset += 1
                        continue
                

                else:
                    offset += 1  # 바이트 이동

            else:
                offset += 1
                continue

    return


def merge_files(file1_path, file2_path, output_file_path):
    # 첫 번째 파일
    with open(file1_path, 'rb') as file1:
        data1 = file1.read()
    
    # 두 번째 파일
    with open(file2_path, 'rb') as file2:
        data2 = file2.read()
    
    # 두 파일의 내용 병합합니다.
    merged_data = data1 + data2
    
    # 새로운 파일에 저장.
    with open(output_file_path, 'wb') as output_file:
        output_file.write(merged_data)
    
    print(f"merge decoding header and frame data. output save on '{output_file_path}'")


def extract_frame_to_jpg(file_path, output_path):
    try:
        # ffplay 명령어를 생성.
        ffmpeg_command = ['ffmpeg','-i', file_path, f'{output_path}%d.jpg']

        # 프레임 저장 명령어 실행.
        subprocess.run(ffmpeg_command, check=True)

    except subprocess.CalledProcessError:
        print("ffmpeg error")
    except Exception as e:
        print(f"error: {str(e)}")



if __name__ == "__main__":
    with open('C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/over_50_bun', 'rb') as f:
        data = f.read()

    ftyp_offset = ftyp(data) #ftyp의 offset을 저장
    print(ftyp_offset)


    hvcC(data, ftyp_offset) #hvcC 파라미터 추출
    first_chunk_offset = stco(data, ftyp_offset) #stco 파라미터 추출
    frame(data, ftyp_offset, first_chunk_offset) #I,P frame 추출

    for index in range(1, len(ftyp_offset) - 1):
        merge_files(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/decoding_header_{index}', f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame_{index}', f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/merge_{index}')#경로 입력 파일명은 변경X
        print(f"complete video_{index}")
        extract_frame_to_jpg(f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/merge_{index}', f'C:/Users/user/Downloads/[CodecsCombine]_Tech_Contest_Report/result/frame/{index}vid_frame_')#경로 입력 파일명은 변경X
        print(f"extract video_{index}")

    
