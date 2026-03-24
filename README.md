# JetBot Orin

## Introduction

<!--[<img src="https://img.shields.io/discord/553852754058280961.svg">](https://discord.gg/Ady6NtF) -->

This is a Jetbot that has been modified from an existing Jetson Nano to use the Jetson Orin Nano. It was built for Waveshare's Jetbot.

## Getting Hardware

You can buy the PCB for this repository from [this link](https://test-bed-robot-for-ai.myshopify.com/products/jetbot-orin?variant=53153578844525).

## Installation Package

```
git clone https://github.com/kimbring2/jetbot.git -b jetbot-orin
```

```
cd jetbot
```

```
sudo python3 setup.py install
```

## Enable Dual CSI Camera

1. **Open Terminal** and run:
   
   bash
   
   ```
   sudo /opt/nvidia/jetson-io/jetson-io.py
   ```

2. Select **Configure Jetson CSI camera slot(s)**.

3. Select the camera type (e.g., `imx219 dual` for Waveshare Binocular camera).

4. Save the changes and select **Reboot** to apply settings. 

## Installing OpenCV with Gstreamer

Visit [this Medium post link](https://medium.com/@erencanbulut/step-by-step-build-opencv-with-gstreamer-on-jetson-orin-nano-ubuntu-22-04-08edfb373c78).

## Register Service

```
cd jetbot/utils
```

```
python create_jupyter_service.py
python create_stats_service.py
```

```
sudo cp jetbot_stats.service /etc/systemd/system/
sudo cp jetbot_jupyter.service /etc/systemd/system/
```

```
sudo chown root:root /etc/systemd/system/jetbot_stats.service
sudo chown root:root /etc/systemd/system/jetbot_jupyter.service

sudo chmod 644 /etc/systemd/system/jetbot_stats.service
sudo chmod 644 /etc/systemd/system/jetbot_jupyter.service
```

```
sudo systemctl daemon-reload

sudo systemctl enable jetbot_stats.service
sudo systemctl enable jetbot_jupyter.service

sudo systemctl start jetbot_stats.service
sudo systemctl start jetbot_jupyter.service

sudo reboot
```

## Checking you did every setting correctly

After 


