import os  
import paho.mqtt.client as paho  
import sys  
import time 
import ev3

mqttc=paho.Client("MIT_EV3")

motorMap={}

tone = ev3.ev3dev.Tone()
touch = ev3.lego.TouchSensor(3)
gyro = ev3.lego.GyroSensor(1)
color = ev3.lego.ColorSensor(2)
motorA = ev3.lego.LargeMotor("A")
motorB = ev3.lego.LargeMotor("B")
motorC = ev3.lego.MediumMotor("C")

GO=True

# 0-100 skala

speedA=80
speedB=80
speedC=80

def on_message(client, userdata, msg):
    #mqttc.loop_stop()
    if userdata!="MIT_EV3":

        global speedA
        global speedB
        global speedC  

        print("MSG: "+msg.payload.decode(encoding='UTF-8')) 

        data=msg.payload.decode(encoding='UTF-8')
        data=data.replace(' ',',')
        data=data.split(',')

        if data[0]=="reset":
            motorA.setup_position_limited(0,50,absolute=True)
            motorB.setup_position_limited(0,50,absolute=True)
            motorC.setup_position_limited(0,50,absolute=True)
            #nem megy vissza 0,0,0 ba
            motorA.run_position_limited(0,50)
            motorB.run_position_limited(0,50)
            motorC.run_position_limited(0,50)

            init_EV3_motor()

        elif data[0]=="relpos":
            #nincs meg tesztelve
            motorA.setup_position_limited(speed[1],absolute=False)
            motorB.setup_position_limited(speed[2],absolute=False)
            motorC.setup_position_limited(speed[3],absolute=False)

        elif data[0]=="goto":
            #abs pos
            #A nal negativ a fel
            #C 0 zart -100 nyit
            motorA.run_position_limited(data[1],speedA)
            motorB.run_position_limited(data[2],speedB)
            motorC.run_position_limited(data[3],speedC)

        elif data[0]=="sd":
            global GO
            GO=False

        elif data[0]=="getdata":

            if data[1]=='all':
                mqttc.publish("EV3",str("TouchSensor: "+str(touch.is_pushed)))
                mqttc.publish("EV3",str("Colorsensor: "+str(color.ref_raw)))
                mqttc.publish("EV3",str("GyroSensor: "+str(gyro.ang_and_rate)))
            elif data[1]==1:
                mqttc.publish("EV3",str("GyroSensor: "+str(gyro.ang_and_rate)))
            elif data[1]==2:
                mqttc.publish("EV3",str("Colorsensor: "+str(color.ambient)))
            elif data[1]==3:
                mqttc.publish("EV3",str("TouchSensor: "+str(touch.is_pushed)))
            else:
                mqttc.publish("EV3",str("TouchSensor: "+str(touch.is_pushed)))
                mqttc.publish("EV3",str("Colorsensor: "+str(color.ref_raw)))
                mqttc.publish("EV3",str("GyroSensor: "+str(gyro.ang_and_rate)))

        elif data[0]=="getpos":

            motorMap=getMotorMap()

            if data[1]=='all':
                mqttc.publish("EV3",str("motorA: "+motorMap["outA"]+"/position"))
                mqttc.publish("EV3",str("motorB: "+motorMap["outB"]+"/position"))
                mqttc.publish("EV3",str("motorC: "+motorMap["outC"]+"/position"))
            elif data[1]=='A':
                mqttc.publish("EV3",str("motorA: "+motorMap["outA"]+"/position"))
            elif data[1]=='B':
                mqttc.publish("EV3",str("motorB: "+motorMap["outB"]+"/position"))
            elif data[1]=='C':
                mqttc.publish("EV3",str("motorC: "+motorMap["outC"]+"/position"))
            else:
                mqttc.publish("EV3",str("motorA: "+motorMap["outA"]+"/position"))
                mqttc.publish("EV3",str("motorB: "+motorMap["outB"]+"/position"))
                mqttc.publish("EV3",str("motorC: "+motorMap["outC"]+"/position"))

            
        elif data[0]=="getstate":

            if data[1]=='all':
                mqttc.publish("EV3",str("motorA: "+motorA.state))
                mqttc.publish("EV3",str("motorB: "+motorB.state))
                mqttc.publish("EV3",str("motorC: "+motorC.state))
            elif data[1]=='A':
                mqttc.publish("EV3",str("motorA: "+motorA.state))
            elif data[1]=='B':
                mqttc.publish("EV3",str("motorB: "+motorB.state))
            elif data[1]=='C':
                mqttc.publish("EV3",str("motorC: "+motorC.state))
            else:
                mqttc.publish("EV3",str("motorA: "+motorA.state))
                mqttc.publish("EV3",str("motorB: "+motorB.state))
                mqttc.publish("EV3",str("motorC: "+motorC.state))

        elif data[0]=="set":

            speedA=data[1]
            speedB=data[2]
            speedC=data[3]
            print(speedA)
            print(speedB)
            print(speedC)

            mqttc.publish("EV3",str("motorA: "+speedA))
            mqttc.publish("EV3",str("motorB: "+speedB))
            mqttc.publish("EV3",str("motorC: "+speedC))

        elif data[0]=="release":
            motorMap=getMotorMap()
            motor_release(motorMap["outA"])  
            motor_release(motorMap["outB"])
            motor_release(motorMap["outC"]) 

        else:
            print("Wrong syntax!!!\n")


def write_command(filename, command):  
    with open(filename, 'w') as f:  
        f.write(command+"\n")

def read_command(filename):  
    with open(filename, 'r') as f:  
        result=f.read()  
        if len(result)>0 and result[-1]=="\n":  
            result=result[0:-1]  
    return result 

def getMotorMap():  
    tempMap={}  
    motors=os.listdir("/sys/class/tacho-motor/")  
    for motor in motors:  
        uport=read_command("/sys/class/tacho-motor/"+motor+"/port_name")  
        tempMap[uport]="/sys/class/tacho-motor/"+motor  
    return tempMap  

def motor_init_reset(motor):  
    write_command(motor+"/stop_command", "hold")
    print("\nHold On\n")

def motor_release(mot):
    write_command(mot+"/stop_command", "coast")
    print("\nHold Off\n")

def init_EV3_motor():

    global speedA
    global speedB
    global speedC

    motorA.reset
    motorB.reset
    motorC.reset

    motorA.stop()
    motorB.stop()
    motorC.stop()

    motorMap=getMotorMap()

    print(motorMap)

    speedA=60
    speedB=60
    speedC=60

    motorA.setup_position_limited(0,speedA,absolute=True)
    motorB.setup_position_limited(0,speedB,absolute=True)
    motorC.setup_position_limited(0,speedC,absolute=True)

    motor_init_reset(motorMap["outA"])  
    motor_init_reset(motorMap["outB"])
    motor_init_reset(motorMap["outC"]) 

    motorA.setup_forever(speedA,speed_regulation=False)
    motorB.setup_forever(speedB,speed_regulation=False)
    motorC.setup_forever(speedC,speed_regulation=False)

    print('EV3 init done')
    tone.play(1000,100)
    time.sleep(1)
    tone.stop()

def on_connect(client, userdata, flags, rc):  
    client.subscribe("EV3")  

def set_MQTT():

    # mqttc.connect("test.mosquitto.org",port=1883)
    mqttc.connect("127.0.0.1",port=1883)  
  
    print("Connected")  
    mqttc.publish("EV3", "EV3 online")  
    print("Published")  
    mqttc.subscribe("EV3")  
    mqttc.loop_start()
    mqttc.on_connect = on_connect  
    mqttc.on_message = on_message

    print('MQTT set')   

    tone.play(1000,100)
    time.sleep(1)
    tone.stop()

def shutdown_session():
    motorMap=getMotorMap()  
    motor_release(motorMap["outA"])  
    motor_release(motorMap["outB"])
    motor_release(motorMap["outC"]) 
    #mqttc.loop_stop()  
    mqttc.disconnect()  
    sys.exit()

if __name__ == "__main__":  
    set_MQTT()
    init_EV3_motor()
    global GO
    while GO:  
      try: 
        time.sleep(1)  
      except KeyboardInterrupt:  
        shutdown_session()
  
  
  
  
 
