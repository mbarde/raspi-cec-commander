# Script to control my raspi via TV remote control
# by Matthias Barde
#
# based on:
# https://www.raspberry-pi-geek.de/ausgaben/rpg/2018/12/per-cec-software-auf-dem-raspi-steuern
# by Bernhard Bablok
#
# libCEC(R) is Copyright (C) 2011-2015 Pulse-Eight Limited.  All rights reserved.
# libCEC(R) is a original work, containing original code.
# libCEC(R) is a trademark of Pulse-Eight Limited.
# License: GPL2 (original libcec-license)
#
# License: GPL3

import cec
import os.path
import pyautogui
import subprocess
import time


class CecController:

    def __init__(self):
        self.log_level = cec.CEC_LOG_WARNING
        self.cecconfig = cec.libcec_configuration()
        self.cecconfig.strDeviceName = 'raspi-player'
        self.cecconfig.bActivateSource = 0
        self.cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_TUNER)
        self.cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT

        self.cecconfig.SetLogCallback(self.process_logmessage)
        # self.cecconfig.SetKeyPressCallback(self.process_key)
        self.cecconfig.SetCommandCallback(self.process_command)

        self.controller = cec.ICECAdapter.Create(self.cecconfig)
        print('libCEC version ' +
              self.controller.VersionToString(self.cecconfig.serverVersion) +
              ' loaded: ' + self.controller.GetLibInfo())

        # search for adapters
        self.com_port = self.get_com_port()

        if self.com_port is None:
            raise EnvironmentError((1, 'No CEC-adapter found'))

        if not self.controller.Open(self.com_port):
            raise EnvironmentError((2, 'could not open CEC-adapter'))

        self.mouseSensibility = 20

    def process_key(self, key, duration):
        print('Remotecontrol key: ' + str(key))
        return 0

    def process_command(self, cmd):
        # decode commans: https://www.cec-o-matic.com/
        print('Command: ' + cmd)
        if cmd == '>> 03:44:00':
            # vendor button down [SELECT]
            pyautogui.click()
        if cmd == '>> 03:44:01':
            # btn down: UP
            pyautogui.moveRel(0, -self.mouseSensibility, duration=0)
        if cmd == '>> 03:44:02':
            # btn down: DOWN
            pyautogui.moveRel(0, self.mouseSensibility, duration=0)
        if cmd == '>> 03:44:03':
            # btn down: LEFT
            pyautogui.moveRel(-self.mouseSensibility, 0, duration=0)
        if cmd == '>> 03:44:04':
            # btn down: RIGHT
            pyautogui.moveRel(self.mouseSensibility, 0, duration=0)
        if cmd == '>> 03:44:4b':
            # btn down: FORWARD
            self.mouseSensibility += 10
            if self.mouseSensibility >= 1000:
                self.mouseSensibility = 1000
        if cmd == '>> 03:44:4c':
            # btn down: BACKWARD
            if self.mouseSensibility > 10:
                self.mouseSensibility -= 10
            else:
                self.mouseSensibility -= 1
            if self.mouseSensibility < 1:
                self.mouseSensibility = 1
        if cmd == '>> 03:44:0d':
            # btn down: EXIT
            pyautogui.press('escape')
        if cmd == '>> 03:44:48':
            # btn down: REWIND
            pyautogui.scroll(-200)
        if cmd == '>> 03:44:49':
            # btn down: FAST FORWARD
            pyautogui.scroll(200)
        if cmd == '>> 03:44:72':
            # btn down: F2 (red):
            self.run_desktop_icon('red.desktop')
        if cmd == '>> 03:44:73':
            # btn down: F3 (green):
            self.run_desktop_icon('green.desktop')
        if cmd == '>> 03:44:74':
            # btn down: F4 (yellow):
            self.run_desktop_icon('yellow.desktop')
        if cmd == '>> 03:44:71':
            # btn down: F1 (blue):
            self.run_desktop_icon('blue.desktop')
        if cmd == '>> 03:44:22':
            # btn down: 2
            pyautogui.press('up')
            pass
        if cmd == '>> 03:44:24':
            # btn down: 4
            pyautogui.press('left')
            pass
        if cmd == '>> 03:44:25':
            # btn down: 5
            pyautogui.press('enter')
            pass
        if cmd == '>> 03:44:26':
            # btn down: 6
            pyautogui.press('right')
            pass
        if cmd == '>> 03:44:28':
            # btn down: 8
            pyautogui.press('down')
            pass
        return 0

    def run_desktop_icon(self, filename):
        desktopDir = '/home/pi/Desktop/'
        filename = desktopDir + filename
        if not os.path.isfile(filename):
            return
        f = open(filename)
        lines = f.readlines()
        f.close()
        execCmdArgs = []
        for line in lines:
            if line.startswith('Exec='):
                execCmdArgs = line[5:].split(' ')
        if len(execCmdArgs) > 0:
            subprocess.Popen(execCmdArgs)

    def process_logmessage(self, level, time, message):
        if level > self.log_level:
            return 0

        if level == cec.CEC_LOG_ERROR:
            levelstr = 'ERROR:   '
        elif level == cec.CEC_LOG_WARNING:
            levelstr = 'WARNING: '
        elif level == cec.CEC_LOG_NOTICE:
            levelstr = 'NOTICE:  '
        elif level == cec.CEC_LOG_TRAFFIC:
            levelstr = 'TRAFFIC: '
        elif level == cec.CEC_LOG_DEBUG:
            levelstr = 'DEBUG:   '

        print(levelstr + '[' + str(time) + ']     ' + message)
        return 0

    def get_com_port(self):
        for adapter in self.controller.DetectAdapters():
            print('CEC adapter:')
            print('port:     ' + adapter.strComName)
            print('vendor:   ' + hex(adapter.iVendorId))
            print('product:  ' + hex(adapter.iProductId))
            return adapter.strComName

        print('Keinen Adapter gefunden')
        return None

    def print_addresses(self):
        addresses = self.controller.GetLogicalAddresses()
        strOut = 'Addresses controlled by libCEC: '
        x = 0
        notFirst = False
        while x < 15:
            if addresses.IsSet(x):
                if notFirst:
                    strOut += ', '
                strOut += self.controller.LogicalAddressToString(x)
                if self.controller.IsActiveSource(x):
                    strOut += ' (*)'
                notFirst = True
            x += 1
        print(strOut)

    def set_active(self):
        self.controller.SetActiveSource()

    def scan_bus(self):
        print('Scanning CEC bus ...')
        strLog = 'CEC bus information:\n\n'
        addresses = self.controller.GetActiveDevices()
        # activeSource = self.controller.GetActiveSource()
        x = 0
        while x < 15:
            if addresses.IsSet(x):
                vendorId = self.controller.GetDeviceVendorId(x)
                physicalAddress = self.controller.GetDevicePhysicalAddress(x)
                active = self.controller.IsActiveSource(x)
                cecVersion = self.controller.GetDeviceCecVersion(x)
                power = self.controller.GetDevicePowerStatus(x)
                osdName = self.controller.GetDeviceOSDName(x)
                strLog += 'Device #' + str(x) + ': ' + self.controller.LogicalAddressToString(x) + '\n'  # noqa: E501
                strLog += 'Address:       ' + str(physicalAddress) + '\n'
                strLog += 'Active Source: ' + str(active) + '\n'
                strLog += 'Vendor:        ' + self.controller.VendorIdToString(vendorId) + '\n'
                strLog += 'CEC Version:   ' + self.controller.CecVersionToString(cecVersion) + '\n'
                strLog += 'OSD Name:      ' + osdName + '\n'
                strLog += 'Power Status:  ' + self.controller.PowerStatusToString(power) + '\n\n\n'
            x += 1
        print(strLog)

    def run(self):
        while True:
            time.sleep(500)
            # command = input('Enter q to quit: ').lower()
            # if command == 'q' or command == 'quit':
            #    return


if __name__ == '__main__':
    controller = CecController()
    controller.run()
