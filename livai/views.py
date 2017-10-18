import requests,os,json,time
from django.shortcuts import render


config  = open('config.txt', 'r')
data= config.read().split('\n')
appid=data[0]
userid=data[1]

def sessiostatus(sessionid):
    headers = {'Authorization' : appid }
    params = {'app_session_id' : sessionid}
    url = 'https://dev.liv.ai/liv_speech_api/session/status/'
    res = requests.get(url, headers = headers, params = params)
    print(res.content)
    docstatus=json.loads(res.content)
    transcribe=docstatus['transcribed_status']
    print(transcribe)
    return transcribe
    


def main(request):
    if request.method=="POST" and request.FILES['audio']:
        files = request.FILES.getlist('audio')

        transcript=[]

        for audio in files:
            filedata=audio.read()
            destination = open('test.mp3', 'wb')
            
            for chunk in audio.chunks():
                destination.write(chunk)
            destination.close()
            
            files = {'audio_file' : open('test.mp3','rb')}
            
            headers = {'Authorization' : appid}
            data = {'user' : userid ,'language' : 'EN','transcribe' : 1} #Change EN to HI if you want transcript in hindi
            
            url = 'https://dev.liv.ai/liv_speech_api/recordings/'
            res = requests.post(url, headers = headers, data = data, files = files)
            print(res.content)
            
            upload_result=json.loads(res.content)
            
            sessionid=upload_result['app_session_id']
            transcribe=False
            
            while transcribe==False:
                time.sleep(3)
                transcribe=sessiostatus(sessionid)
                
            headers = {'Authorization' : appid }
            params = {'app_session_id' : sessionid  }
            url = 'https://dev.liv.ai/liv_speech_api/session/transcriptions/'
            res = requests.get(url, headers = headers, params = params)
            t=json.loads(res.content)
            print(t)
            transcript.append(t['transcriptions'][0]['utf_text'])

        print(transcript)    
        return render(request,"index.html",{'results':transcript})

    return render(request,"index.html")

