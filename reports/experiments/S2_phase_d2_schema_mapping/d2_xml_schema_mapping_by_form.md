# D2 XML Schema Mapping by Form

For each base form encountered in D1+D2 sample, the table below lists the observed XML structure summary and candidate fields for parser implementation.

Reference XML samples are stored under `data/acquired/round4/s2_dart_body_d1/raw_xml/` and `data/acquired/round4/s2_dart_body_d2/raw_xml/`.

## 감자결정(자율공시)

- Sample rcept_no: `20200820800032`
- XML size: 16,576 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타시장안내              (업종변경 안내)

- Sample rcept_no: `20240628901264`
- XML size: 4,821 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타시장안내 (추가상장 유예 관련 안내)

- Sample rcept_no: `20250923800522`
- XML size: 8,624 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타안내사항(안내공시) (보통주 의무보유(보호예수)기간 만료))

- Sample rcept_no: `20240722800247`
- XML size: 4,426 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타안내사항(안내공시) (주성코퍼레이션 보통주 보호예수기간 만료안내)

- Sample rcept_no: `20250106800181`
- XML size: 5,509 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타안내사항(안내공시)(바이오노트 보통주 의무보유(보호예수)기간 만료 안내)

- Sample rcept_no: `20231227800077`
- XML size: 4,670 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타안내사항(안내공시)(보통주 의무보유(보호예수)기간 만료)

- Sample rcept_no: `20230619800367`
- XML size: 9,374 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 기타안내사항(안내공시)(보호예수기간 만료 안내)

- Sample rcept_no: `20180122800260`
- XML size: 5,357 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 단일판매ㆍ공급계약체결

- Sample rcept_no: `20250930900860`
- XML size: 9,941 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 소송등의판결ㆍ결정(일정금액이상의청구)

- Sample rcept_no: `20240628901311`
- XML size: 11,198 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 신주인수권행사가액의조정

- Sample rcept_no: `20250930900843`
- XML size: 9,533 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 유무상증자결정

- Sample rcept_no: `20201103800004`
- XML size: 41,537 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 유상증자결정

- Sample rcept_no: `20250131800841`
- XML size: 27,829 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 임원ㆍ주요주주특정증권등소유상황보고서

- Sample rcept_no: `20200727000040`
- XML size: 22,838 bytes
- Has DOCUMENT root: True
- SECTION count: 7 / TABLE count: 16 / TH count: 38 / TD count: 52
- Title: `1. ����ȸ�翡 ���� ����`
- Distinct TH labels (truncated to 40):
  - Ư�����ǵ�
  - Ư�����ǵ��� ����
  - Ư�����ǵ��� ��������&cr;[A+I / J+I-(F+G+H)��] �� 100
  - Ư�����ǵ���&cr;��(��)
  - Ư�����ǵ���&cr;����
  - �ֱ�
  - �ֱ��� ��������&cr;(A / J) �� 100
  - �ּ�&cr;(��)
  - �ֽļ�(��)
  - �ֽĿ� Ư�����ǵ��� ��&cr;(B+C+D+E+F+G+H=I)
  - �� ��
  - �� �� �� �� �� (��)
  - ��Ÿ
  - ��ȯ&cr;��ä��
  - ���/ó��&cr;�ܰ�(��)**
  - ����
  - ����&cr;(%)
  - ����&cr;�μ��Ǻ�&cr;��ä��
  - ����&cr;�μ�����&cr;ǥ�õȰ�
  - ����&cr;��Ź&cr;����
  - ����(%)
  - �����ֽ� �Ѽ�&cr;(J)
  - ������
  - ������&cr;�ۼ� ������
  - ������*
  - ��������
  - ��������(%)
  - ����������&cr;��ä��

## 자기주식처분결과보고서

- Sample rcept_no: `20231212000273`
- XML size: 15,755 bytes
- Has DOCUMENT root: True
- SECTION count: 11 / TABLE count: 11 / TH count: 35 / TD count: 34
- Title: `1. 발행인의 명칭 및 주소`
- Distinct TH labels (truncated to 40):
  - 1주당처분가액
  - 계(A + B)
  - 계약금액
  - 고유번호
  - 금  액
  - 금융투자업자
  - 기타주식
  - 매도위탁 증권회사
  - 법제165조의3의규정에 의한 보유상황(A)
  - 법제165조의3의신탁계약등에 의한 보유상황(B)
  - 보통주식
  - 비율
  - 수  량
  - 수량
  - 일  자
  - 일치여부
  - 종  류
  - 주문수량
  - 주식의종　류
  - 차이발생시 사유
  - 처분가액총　　액
  - 처분대상
  - 처분수량
  - 처분예정주식(주)
  - 처분주식 총수(주)
  - 총가액
- candidate_date_fields: ['일  자', '일치여부']
- candidate_amount_fields: ['계약금액']
- candidate_share_fields: ['보통주식', '수량', '주문수량', '처분수량']

## 자기주식취득결과보고서

- Sample rcept_no: `20240912000423`
- XML size: 37,434 bytes
- Has DOCUMENT root: True
- SECTION count: 11 / TABLE count: 14 / TH count: 41 / TD count: 57
- Title: `1. 발행인의 명칭 및 주소`
- Distinct TH labels (truncated to 40):
  - 1주당취득가액
  - 계(A+B)
  - 계약금액
  - 고유번호
  - 금  액
  - 금융투자업자
  - 기타주식
  - 매수위탁 증권회사
  - 법제165조의3의 규정에 의한 보유상황(A)
  - 법제165조의3의신탁계약에 의한 보유상황(B)
  - 변동사유
  - 보유주식 변동내역
  - 보통주식
  - 비율
  - 성  명
  - 수  량
  - 수량
  - 일  자
  - 일치여부
  - 종  류
  - 주문수량
  - 주식의 종류
  - 차이발생시 사유
  - 총가액
  - 취득가액총    액
  - 취득보고일
  - 취득수량
  - 취득예정주식(주)
  - 취득종료일
  - 취득주식총수(주)
- candidate_date_fields: ['일  자', '일치여부', '취득보고일', '취득종료일']
- candidate_amount_fields: ['계약금액']
- candidate_share_fields: ['보통주식', '수량', '주문수량', '취득수량']

## 자기주식취득결정

- Sample rcept_no: `20220712800304`
- XML size: 37,142 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 전환사채(해외전환사채포함)발행후만기전사채취득

- Sample rcept_no: `20230131900511`
- XML size: 8,327 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 전환청구권행사

- Sample rcept_no: `20200715900389`
- XML size: 18,800 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 주식등의대량보유상황보고서(일반)

- Sample rcept_no: `20250930000781`
- XML size: 86,309 bytes
- Has DOCUMENT root: True
- SECTION count: 26 / TABLE count: 49 / TH count: 139 / TD count: 126
- Title: `제1부 보고의 개요`
- Distinct TH labels (truncated to 40):
  - 계(H+I+J)
  - 계(주)
  - 계약 상대방
  - 계약기간
  - 계약의종류
  - 계약체결(변경)일
  - 계정별 내역
  - 고객계정(주)
  - 관 계
  - 관계
  - 교환사채권
  - 구분
  - 국적
  - 기타
  - 기타(J)
  - 담보유지비율
  - 대상 집합투자기구
  - 대출금액
  - 명칭
  - 발행회사와의 관계
  - 변동 내역
  - 변동일*
  - 변동전
  - 변동후
  - 보고서작성기준일
  - 보고자
  - 보고자와의관계
  - 보고자와의구체적 관계
  - 보유비율(%)
  - 보유잠재주식의 수(a1+a2+B+C+D+E+F+G=H)
  - 보유주식등의 내역
  - 본인 성명
  - 비 고
  - 비고
  - 비율
  - 비율(%)
  - 사업자등록번호 등
  - 생년월일 또는사업자등록번호 등
  - 생년월일 또는사업자등록번호등
  - 생년월일또는사업자등록번호 등
- candidate_date_fields: ['계약체결(변경)일', '변동일*', '보고서작성기준일', '생년월일 또는사업자등록번호 등', '생년월일 또는사업자등록번호등', '생년월일또는사업자등록번호 등']
- candidate_amount_fields: ['대출금액']
- candidate_share_fields: ['발행회사와의 관계']
- candidate_effective_date_fields: ['보고서작성기준일']

## 주식소각결정

- Sample rcept_no: `20260209800783`
- XML size: 9,406 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 주요사항보고서(감자결정)

- Sample rcept_no: `20260316001121`
- XML size: 15,842 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 6 / TH count: 0 / TD count: 69
- Title: `주요사항보고서 / 거래소 신고의무 사항`

## 주요사항보고서(무상증자결정)

- Sample rcept_no: `20221208800248`
- XML size: 9,813 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 4 / TH count: 0 / TD count: 68

## 주요사항보고서(신주인수권부사채권발행결정)

- Sample rcept_no: `20200928000303`
- XML size: 37,492 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 15 / TH count: 4 / TD count: 116
- Title: `�ֿ���׺����� / �ŷ��� �Ű��ǹ� ����`
- Distinct TH labels (truncated to 40):
  - ȸ�� �Ǵ�&cr;�ִ����ֿ��� ����
  - ���� ����ڸ�
  - ����Ǹ�(���ڵ��)&cr;�Ѿ�(��)

## 주요사항보고서(유무상증자결정)

- Sample rcept_no: `20230223000782`
- XML size: 43,125 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 21 / TH count: 12 / TD count: 181
- Title: `정 정 신 고 (보고)`
- Distinct TH labels (truncated to 40):
  - 구분
  - 상세내역
  - 정 정 전
  - 정 정 후
  - 정정사유
  - 청약대상자
  - 청약일
  - 청약취급처
  - 항  목
- candidate_date_fields: ['청약일']

## 주요사항보고서(유상증자결정)

- Sample rcept_no: `20180306000559`
- XML size: 17,668 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 13 / TH count: 10 / TD count: 68
- Title: `�ֿ���׺����� / �ŷ��� �Ű��ǹ� ����`
- Distinct TH labels (truncated to 40):
  - ȸ�� �Ǵ�&cr;�ִ����ֿ��� ����
  - �� ��
  - ��3�ڹ��� �ٰŰ� �Ǵ� ��������
  - ��3�ڹ��� �����
  - ��3�ڹ��� ������ ����
  - ���ڰ��� ���� 6���̳� �ŷ����� �� ��ȹ
  - �����ֽļ� (��)
  - ��������

## 주요사항보고서(자기주식처분결정)

- Sample rcept_no: `20210805800349`
- XML size: 23,061 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 6 / TH count: 10 / TD count: 234
- Distinct TH labels (truncated to 40):
  - ó��(-)
  - �Ұ�(-)
  - �ֽ��� ����
  - �⸻����
  - ���
  - ���(+)
  - ���ʼ���
  - ���� ����
  - �����

## 주요사항보고서(자기주식취득결정)

- Sample rcept_no: `20240708000261`
- XML size: 32,312 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 12 / TH count: 18 / TD count: 113
- Title: `정 정 신 고 (보고)`
- Distinct TH labels (truncated to 40):
  - 금  액
  - 기말수량
  - 기초수량
  - 변동 수량
  - 비고
  - 소각(-)
  - 정 정 전
  - 정 정 후
  - 정정사유
  - 주식의 종류
  - 처분(-)
  - 취득(+)
  - 취득방법
  - 항  목
- candidate_share_fields: ['기말수량', '기초수량', '변동 수량']

## 주요사항보고서(자기주식취득신탁계약체결결정)

- Sample rcept_no: `20220323001038`
- XML size: 25,660 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 10 / TH count: 13 / TD count: 93
- Title: `�ֿ���׺����� / �ŷ��� �Ű��ǹ� ����`
- Distinct TH labels (truncated to 40):
  - ó��(-)
  - �Ұ�(-)
  - �ֽ��� ����
  - �⸻����
  - ��  ��
  - ���
  - ���(+)
  - ���ʼ���
  - ���� ����
  - �����

## 주요사항보고서(자기주식취득신탁계약해지결정)

- Sample rcept_no: `20250131000515`
- XML size: 27,265 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 8 / TH count: 10 / TD count: 89
- Title: `주요사항보고서 / 거래소 신고의무 사항`
- Distinct TH labels (truncated to 40):
  - 기말수량
  - 기초수량
  - 변동 수량
  - 비고
  - 소각(-)
  - 주식의 종류
  - 처분(-)
  - 취득(+)
  - 취득방법
- candidate_share_fields: ['기말수량', '기초수량', '변동 수량']

## 주요사항보고서(전환사채권발행결정)

- Sample rcept_no: `20210820000414`
- XML size: 60,256 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 21 / TH count: 9 / TD count: 372
- Title: `�� �� �� �� (����)`
- Distinct TH labels (truncated to 40):
  - ȸ�� �Ǵ�&cr;�ִ����ֿ��� ����
  - ��  ��
  - �� �� ��
  - ���� ����ڸ�
  - ����Ǹ�(���ڵ��)&cr;�Ѿ�(��)
  - ��������

## 주요사항보고서(회사분할결정)

- Sample rcept_no: `20200225000219`
- XML size: 97,197 bytes
- Has DOCUMENT root: True
- SECTION count: 2 / TABLE count: 7 / TH count: 0 / TD count: 460
- Title: `주요사항보고서 / 거래소 신고의무 사항`

## 주요사항보고서(회사합병결정)

- Sample rcept_no: `20211230000663`
- XML size: 154,535 bytes
- Has DOCUMENT root: True
- SECTION count: 5 / TABLE count: 27 / TH count: 4 / TD count: 1466
- Title: `�ֿ���׺����� / �ŷ��� �Ű��ǹ� ����`
- Distinct TH labels (truncated to 40):
  - ����
  - ����&cr;(�պ�����)
  - ����&cr;(���պ�����)

## 철회신고서

- Sample rcept_no: `20231019000356`
- XML size: 4,187 bytes
- Has DOCUMENT root: True
- SECTION count: 0 / TABLE count: 2 / TH count: 0 / TD count: 29

## 철회신고서((주)제이알글로벌위탁관리부동산투자회사)

- Sample rcept_no: `20260205000602`
- XML size: 4,679 bytes
- Has DOCUMENT root: True
- SECTION count: 0 / TABLE count: 2 / TH count: 0 / TD count: 27

## 철회신고서(㈜미래에셋글로벌위탁관리부동산투자회사)

- Sample rcept_no: `20220711000424`
- XML size: 4,611 bytes
- Has DOCUMENT root: True
- SECTION count: 0 / TABLE count: 2 / TH count: 0 / TD count: 31

## 최대주주변경을수반하는주식담보제공계약체결

- Sample rcept_no: `20230131900695`
- XML size: 24,091 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0

## 회사합병결정

- Sample rcept_no: `20240717800627`
- XML size: 22,793 bytes
- Has DOCUMENT root: False
- SECTION count: 0 / TABLE count: 0 / TH count: 0 / TD count: 0
