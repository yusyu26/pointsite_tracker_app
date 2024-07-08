import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime,date

#広告のURL
sites=[
    'https://pc.moppy.jp/ad/detail.php?site_id=149052&track_ref=sea',
    'https://pc.moppy.jp/ad/detail.php?site_id=102162&track_ref=car',
    'https://pc.moppy.jp/ad/detail.php?site_id=119456&track_ref=sea',
    'https://pc.moppy.jp/ad/detail.php?site_id=144526&track_ref=car',
    'https://pc.moppy.jp/ad/detail.php?site_id=140425&track_ref=sea',
    'https://pc.moppy.jp/ad/detail.php?site_id=111069&track_ref=sea',
    'https://pc.moppy.jp/ad/detail.php?site_id=149995'
    ]#サイト追加時には要変更

#CSVファイル    
file='point_data.csv'

# データをCSVファイルに保存する関数
def save_data_to_csv(data):
    data.to_csv(file, index=False)
    
# CSVファイルからデータを読み込む関数
def load_data_from_csv():
    return pd.read_csv(file)
    
#広告名とポイント数をスクレイピングする関数
def scrape_site(url):
    res =requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')
    point = soup.find('em',{'class':'a-item__point--now'}).text
    name = soup.find('h1',{'class':'a-item__h1'}).text
    return point,name

# ポイント数を整数に変換する関数
def convert_point_string(point_str):
    return int(point_str.replace(',', '').replace('P', ''))


#メイン関数
def main():
    #タイトル
    st.title('PointSite tracker')
    #データの読み込み
    df = load_data_from_csv()
    #日付の取得
    today = datetime.today().date()
    
    #前回の更新から日付が変わっていればスクレイピング実行
    if df.iloc[-1][0] != str(today):
        cnt=0
        namebox = []
        for site in sites:
            point,name = scrape_site(site)
            #デバッグ用案件名一覧
            namebox.append(name)
            #案件ごとに日付と取得したポイント数を入れる
            new_data = pd.DataFrame({
                'date' : today,
                site : [convert_point_string(point)]
                })
            if cnt == 0:
                new_df =new_data
                cnt = 1
            else:
                new_df = pd.merge(new_df, new_data, on='date',how='outer')
        #取得したデータを結合
        df = pd.concat([df,new_df])
        #データを保存
        save_data_to_csv(df)
    
    #リストの準備
    now = []
    before = []
    diff = []
    mx = []
    #案件ごとの現在のポイント,前日のポイント,前日比,過去最高値を算出
    for i in range(len(sites)):
        #現在ポイント
        now.append(str(df.iloc[-1][1+i])+'P')
        #前日ポイント
        before.append(str(df.iloc[-2][1+i])+'P')
        #前日比
        diff.append('{:+}'.format(int(df.iloc[-1][1+i])-int(df.iloc[-2][1+i]))+'P')
        #最高値
        A = []
        for j in range(len(df.iloc[:,[1]])):
            A.append(int(df.iloc[j][1+i]))
        mx.append(str(max(A))+'P')

    #表示用のデータフレームを作成
    last_data = pd.DataFrame({
                    '現在のポイント数' : now,
                    '前日のポイント数' : before,
                    '前日比' : diff,
                    '過去最高値' : mx},
                    index=['三井住友カード（NL）',
                           'エポスカード【最短4日付与】',
                           'U-NEXT[31日間無料お試し]',
                           'マネックス証券★100円から取引可能★',
                           'JCB CARD W/JCB CARD W plus L(39歳以下限定)',
                           '楽天証券','JALカード(VISA) navi 【学生専用】'])#サイト追加時には要変更
    
    #表示
    st.write(last_data)
    #更新ボタン
    st.button('更新')
    st.write('最終更新時刻:' + str(datetime.today().replace(microsecond=0)))
    
if __name__ == '__main__':
    main()