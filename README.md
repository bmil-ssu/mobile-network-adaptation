# mobility-deepRL
implementation for mobility


1. 실험 준비
실험 장비 및 도구:  Xbee Pro S2C 6개, 라즈베리파이 6개, 노트북, python, XCTU 
실험 장소 : 장애물이 없고 경사도 없는 직선거리, 만약 장애물이 아예 없는 장소가 불가능 하다면 장애 요인이 각 거리마다 비슷한 확률로 나타나는 장소도 가능

2. 실험 전 세팅
1) 6개의 Xbee 모듈을 XCTU 라는 프로그램을 이용하여 초기 설정을 진행한다. 6개 모두 XCTU 펌웨어의 Function set을 ZIGBEE TH PRO로 설정한다.
3) 6개의 ID (PAN ID) 라는 요소를 같은 숫자로 수정한다. (본 실험에서는 1234로 설정하였다.)
2) NI(Node Identifier) 라는 요소를 수정하여 각 Xbee 모듈의 이름을 설정해준다.
4) coordinator 역할을 하는 Xbee는 CE (Coordinator Enable)이라는 요소를 Enabled[1]로 설정하고, DL(Destination Address Low)는 FFFF로 설정하여 Radio Broadcast Mode로 만들어준다.
3) 나머지 Xbee는 CE를 Disabled[0]로 JV(Channel Verification)이라는 요소는 Enabled[1]로 설정하고, SM(Sleep Mode) 라는 요소는 No Sleep (Router) [0]로 설정하고 마지막으로 DL이라는 요소를 0으로 설정한다.

3. 야외 실험 방법
1) 미리 세팅한 xbee를 라즈베리파이 port에 꽂고 직선거리에 배치한다. 본 실험에서는 coordinator 노드를 시작으로 115m, 230m, 300m, 360m, 430m에 수신 노드를 하나씩 놓았다.
2) coordinator 노드에서 본 소프트웨어 로직을 실행시킨 후, 실험결과가 나올 때까지 약 1시간 정도를 기다린다.
3) 실험이 끝난 후에, 코드 파일이 저장된 동일 위치에 생긴 ‘real_data_final.csv’ 파일을 통해 실험 결과를 확인한다.
