# Nokia router's card auto-provisioning

The goal is simple - whenever a new card is inserted into the router, it should be provisioned automatically without any engineering force intervention. To achieve the goal, I am using 2 frameworks napalm-logs and Stackstorm. Napalm-logs grabs syslog messages and transform it to one common style (when multiple router vendors present in the network) and Stackstorm triggers proper action whenever syslog event matches the criteria given in the sensor/rule.

For purpose of this example, I will be looking for MDA cards insertion into the IOM module (Syslog events). This make sense if you are not preconfiguring your cards before they are equipped. For example, you could make some assumptions about IOM-s arrangements in your routers to provide redundancy and guarantee proper failover scenarios but maybe not for MDA. So, let's assume you don't care and don't plan in advance if MDA should go into slot 1 or slot 2 of the IOM. This means Field Engineer can insert the card either into the first or second slot. In such cases, you cannot tell in advance what MDA card type will be inserted into particular slot, so you need to wait with card provisioning until the card is really inserted into the router.

Our starting point on R1:

```
A:R1# show mda 

===============================================================================
MDA Summary
===============================================================================
Slot  Mda   Provisioned Type                            Admin     Operational
                Equipped Type (if different)            State     State
-------------------------------------------------------------------------------
1     1     m5-1gb-sfp-b                                up        up
      2     (not provisioned)                           up        unprovisioned
                m5-1gb-sfp-b                                          
===============================================================================
```

### Napalm-logs

You can start with napalm-logs from [here](http://napalm-logs.readthedocs.io/en/latest/) and have a quick view what's the overall concept. There are Juniper, Cisco and other profiles defined but not for Nokia. So, let's follow the doc-s and add new profile inside 'napalm_logs/config' dir. That is where all device and message types are defined. Inside configs dir I will create new dir called sros and a file called 'init.yml'. It should look like this: 

```
prefixes:
  - time_format: "%b %d %H:%M:%S"
    values:
      date: (\w+\s+\d+)
      time: (\d\d:\d\d:\d\d)
      hostip: (\d+.\d+.\d+.\d+)
      hostPrefix: (\S+)
      processName: ([\w\d]+)
      processId: (\d+)
      tag: (\S+)
      tag2: (.*)?
    line: "{date} {time} {hostip} {hostPrefix}: {processId} {processName} {tag} [{tag2}]:"
```

In the same folder I need to create message-type-file that simply will match syslog event saying that MDA card was inserted. You can check napalm-logs for more specific info about construction of those files. I will call it MODULE_INSERTED.yml:

```
messages:
  - error: MODULE_INSERTED
    tag: CHASSIS-MINOR-tmnxEqCardInserted-2002
    values:
      component: (\w+)
    line: "Class {component} Module : inserted"
    model: NO_MODEL
    mapping:
      variables:
        hardware-state//component//{component}//name: component
      static:
        hardware-state//component//{component}//state//alarm-state: RED
        hardware-state//component//{component}//state//alarm-reason: "MODULE INSTERTED"
        hardware-state//component//{component}//class: CHASSIS
``` 

Those 2 files should be enough to grab syslog message generated from Nokia router and transform it to proper format. In this example I need to simulate card insertion into the Nokia router. Because I work on VM-s one way to do it(the only one I can think of) is to reboot the VM. As soon as the VM comes back online after the reboot I should see Syslog messages on my localhost:

```
Mar 23 14:01:21 192.168.122.100 R1: 3602 Base CHASSIS-MINOR-tmnxEqCardInserted-2002 [Card 1]:  Class IO Module : inserted
Mar 23 14:01:24 192.168.122.100 R1: 3604 Base CHASSIS-MINOR-tmnxEqCardInserted-2002 [Mda 1/1]:  Class MDA Module : inserted
Mar 23 14:01:24 192.168.122.100 R1: 3605 Base CHASSIS-MINOR-tmnxEqCardInserted-2002 [Mda 1/2]:  Class MDA Module : inserted
```

We should reveive 3 messages in this example related to card insertion. One for IOM card and 2 for MDA-s. At this point I can change configuration of my router/VM so that it sends Syslog messages to some custom port - 10514 in this example:

```
A:R1>config>log>syslog# info 
----------------------------------------------
            address 192.168.122.1
            log-prefix "R1"
            port 10514
----------------------------------------------
```

After changing the router config, you can check if napalm-logs are matching the syslog messages by running following command:

```
sudo napalm-logs -a 192.168.122.1 --disable-security -p 10514 --publisher cli
```

Address and port is the place where my router is configured to send syslog messages. To simplify example, I am also disabling security and publish the output to CLI. Before going further this should be the first step of testing. Check if your 'expressions' from MODULE_INSERTED.yml and init.yml are matching syslog message. You should see something like this:

```
~$ sudo napalm-logs -a 192.168.122.1 --disable-security -p 10514 --publisher cli
��host��
        yang_message��hardware-state��  component��IO��state��
.
..

```

In next step you should check if you can receive message generated by napalm-logs. Now you don't want to publish message to CLI but passed it further. Further means towards client, which in this example is Stackstorm. Before starting with st2 let's check if simple python client can receive our message. Run the command:

```
sudo napalm-logs -a 192.168.122.1 --disable-security -p 10514
```

The publisher is no longer CLI and by default, that napalm-logs is using is zmq messaging system. You need to install pyzmq to send/receive such messages. To check if your message reaches your client, just run the script from python interpreter(taken from napalm-logs):

```
import zmq
import napalm_logs.utils

server_address = '127.0.0.1'  # --publish-address
server_port = 49017           # --publish-port

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                               port=server_port))
socket.setsockopt(zmq.SUBSCRIBE, '')

while True:
    raw_object = socket.recv()
    print(napalm_logs.utils.unserialize(raw_object))
```

Address and port are default in this example as I am operating on my localhost only, but you can modify those values according to your needs.
Whenever the message is received you should see something like this:

```
>>> while True:
...     raw_object = socket.recv()
...     print(napalm_logs.utils.unserialize(raw_object))
... 
{'yang_message': {'hardware-state': {'component': {'IO': {'state': {'alarm-reason': 'MODULE INSTERTED', 'alarm-state': 'RED'}, 'name': 'IO', 'class': 'CHASSIS'}}}}, 'message_details': {'processId': '5602', 'severity': 3, 'tag2': 'Card 1', 'facility': 23, 'hostPrefix': 'R1', 'time': '14:52:35', 'pri': '187', 'processName': 'Base', 'tag': 'CHASSIS-MINOR-tmnxEqCardInserted-2002', 'hostip': '192.168.122.100', 'date': 'Mar 23', 'message': 'Class IO Module : inserted'}, 'facility': 23, 'ip': '192.168.122.100', 'error': 'MODULE_INSERTED', 'host': None, 'yang_model': 'NO_MODEL', 'timestamp': 1521816755, 'os': 'sros', 'severity': 3}
{'yang_message': {'hardware-state': {'component': {'MDA': {'state': {'alarm-reason': 'MODULE INSTERTED', 'alarm-state': 'RED'}, 'name': 'MDA', 'class': 'CHASSIS'}}}}, 'message_details': {'processId': '5604', 'severity': 3, 'tag2': 'Mda 1/1', 'facility': 23, 'hostPrefix': 'R1', 'time': '14:52:38', 'pri': '187', 'processName': 'Base', 'tag': 'CHASSIS-MINOR-tmnxEqCardInserted-2002', 'hostip': '192.168.122.100', 'date': 'Mar 23', 'message': 'Class MDA Module : inserted'}, 'facility': 23, 'ip': '192.168.122.100', 'error': 'MODULE_INSERTED', 'host': None, 'yang_model': 'NO_MODEL', 'timestamp': 1521816758, 'os': 'sros', 'severity': 3}
{'yang_message': {'hardware-state': {'component': {'MDA': {'state': {'alarm-reason': 'MODULE INSTERTED', 'alarm-state': 'RED'}, 'name': 'MDA', 'class': 'CHASSIS'}}}}, 'message_details': {'processId': '5605', 'severity': 3, 'tag2': 'Mda 1/2', 'facility': 23, 'hostPrefix': 'R1', 'time': '14:52:38', 'pri': '187', 'processName': 'Base', 'tag': 'CHASSIS-MINOR-tmnxEqCardInserted-2002', 'hostip': '192.168.122.100', 'date': 'Mar 23', 'message': 'Class MDA Module : inserted'}, 'facility': 23, 'ip': '192.168.122.100', 'error': 'MODULE_INSERTED', 'host': None, 'yang_model': 'NO_MODEL', 'timestamp': 1521816758, 'os': 'sros', 'severity': 3}
``` 

Now we can build our client to receive the messages published from napalm-logs.


### Stackstorm Sensor

The thing I like the most about Stackstorm is the option of triggering actions based on different events. The events can be probably anything you can think of, as long as you can define sensor which will understand the event. In our example we need sensor that will understand zmq messages published from napalm logs. Sensors in Stackstorm are written in python, but before writing our own Sensor let's check the community [stackstorm exchange](https://exchange.stackstorm.org/). Luckily there is Stackstorm sensor already created that should serve our needs. 


Without going into the details, just a couple of steps to set up new senor. It should be created within new pack so let's move to Stackstorm dir with pack-s and clone the repo:

```
cd /opt/stackstorm/packs/
git clone https://github.com/StackStorm-Exchange/stackstorm-napalm_logs.git

```

Several files were cloned and we need to do some modification so that files are in-sync with our scenario.

First, I will shorten the name of the dir, so when I register new pack it will have shorter name - just for my convenience. I am also changing permissions so it's similar as other packs generated by default - not sure if needed:

'''
sudo mv stackstorm-napalm_logs napalm_logs
sudo chown -R root:st2packs napalm_logs
'''

We also need to add config files for our pack in '/opt/stackstorm/configs/' - according to the documentation napalm_logs.yaml and napalm-logs.crt. This napalm_logs.yaml name, should correspond to our pack name that we will register soon. Inside the file put this:

```
---
server_address: 127.0.0.1
server_port: 49017
auth_address: 127.0.0.1
auth_port: 49018
certificate_file: /opt/stackstorm/configs/napalm-logs.crt
```
Change ownership of the napalm_logs.yaml in '/opt/stackstorm/configs/' to be:

```
sudo chown st2:st2 napalm_logs.yaml
```

Again, parameters from napalm_logs.yaml are defaults, so you may need to change those in order to receive messages published from napalm-logs. We also need to create certification_file according to our config file, so create it within config dir and leave it empty or add some comment.

```
touch napalm-logs.crt
```

We are not using certifications in this example, but it's recommend option. 
Because we disabled security, we also need to do some small changes in our sensor that sits in '/opt/stackstorm/packs/napalm_logs/sensors/napalm_logs_client.py':

```
import zmq
import napalm_logs.utils

from st2reactor.sensor.base import Sensor


class NapalmLogsSensor(Sensor):

    def __init__(self, sensor_service, config):

        super(NapalmLogsSensor, self).__init__(sensor_service, config)

        self._server_address = self.config.get('server_address')  # --publish-address
        self._server_port = self.config.get('server_port')           # --publish-port
        self._auth_address = self.config.get('auth_address')    # --auth-address
        self._auth_port = self.config.get('auth_port')             # --auth-port
        self._certificate = self.config.get('certificate_file')  # --certificate

    def setup(self):

        # Using zmq
        context = zmq.Context()
        # pylint: disable=no-member
        self.socket = context.socket(zmq.SUB)

        # override OS tcp keepalive settings to keep socket open
        # pylint: disable=no-member
        self.socket.setsockopt(zmq.TCP_KEEPALIVE, 1)
        # pylint: disable=no-member
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 300)
        # pylint: disable=no-member
        self.socket.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 300)

        self.socket.connect('tcp://{address}:{port}'.format(address=self._server_address,
                                                            port=self._server_port))
        # pylint: disable=no-member
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')

        # self.auth = napalm_logs.utils.ClientAuth(self._certificate,
        #                                          address=self._auth_address,
        #                                          port=self._auth_port)

    def run(self):

        while True:
            # raw_object = self.socket.recv()
            # decrypted = self.auth.decrypt(raw_object)
            # self._sensor_service.dispatch(trigger='napalm_logs.log', payload=decrypted)
            raw_object = napalm_logs.utils.unserialize(self.socket.recv())
            self._sensor_service.dispatch(trigger='napalm_logs.log', payload=raw_object)

    def cleanup(self):
        pass

    def add_trigger(self, trigger):
        # This method is called when trigger is created
        pass

    def update_trigger(self, trigger):
        # This method is called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # This method is called when trigger is deleted
        pass

```

and the napalm_logs_client.yaml from '/opt/stackstorm/packs/napalm_logs/sensors/':

```
---
class_name: "NapalmLogsSensor"
entry_point: "napalm_logs_client.py"
description: "Napalm-logs as a sensor. Rendered logs are dispatched as triggers."
trigger_types:
  -
    name: "log"
    description: "Log instance from Napalm-logs"
    payload_schema:
      type: "object"
      properties:
        payload:
          type: "object"
```

We should be ready to register our pack by running command:

```
sudo st2 reload --register-all
```

Whenever some errors pop up, either while config files, trigger or sensor registering - sensor will not work. So, while registering you really should not see any errors. You can always isolate problems by registering part of your pack with --register-actions or triggers, rules etc.

You should see both new sensor as well as new trigger available from stackstorm list. Just check if st2 lists napalm_logs.NapalmLogsSensor and napalm_log.log (trigger).
Check if sensor is enabled: 

```
st2 sensor get napalm_logs.NapalmLogsSensor
```

and you should be good to receive a napalm log messages.

We have not defined rule nor action yet, but we can already verify if sensor works correctly. To do so first run napalm-logs, then generate syslog event by simulating card insertion(VM reboot). If message was properly consumed by sensor you should see it by running:

```
st2 trigger-instance list --trigger=naplam_logs.log
.
..
| 5ab50c429eb0c904913e74a7 | napalm_logs.log | Fri, 23 Mar 2018 14:16:34 UTC | processed         |
| 5ab50c459eb0c904913e74ab | napalm_logs.log | Fri, 23 Mar 2018 14:16:37 UTC | processed         |
| 5ab50c459eb0c904913e74ac | napalm_logs.log | Fri, 23 Mar 2018 14:16:37 UTC | processed         |
+--------------------------+-----------------+-------------------------------+-------------------+
```

Now we need to trigger some action.


### Stackstorm Actions and Rules

We still need some logic that will decide if action is required and validate if provisioning is really needed. Before creating Stackstorm action let's add new Rule in './rules/' directory in our napalm_logs pack. It should be yaml format and I call it napalm_logs_mda.yaml:

```
---
name: "napalm_logs_mda"                      
pack: "napalm_logs"                       
description: "Triggers action when mda inserted."       
enabled: true                          

trigger:                               
  type: "napalm_logs.log"
  parameters: {}

criteria:                             
  trigger.message_details.tag2:
    type: "startswith"
    pattern : "Mda"

action:                                
  ref: "napalm_logs.mda_provisioning"
  parameters:
    hostip: "{{ trigger.message_details.hostip }}"
    mda_tag: "{{ trigger.message_details.tag2 }}"
    hostname: "{{ trigger.message_details.hostPrefix }}"
```

This rule grabs triggers that our sensor is generating, process it through its criteria section and whenever pattern is matched, 'some' action section is run. We have not yet created action that is referenced in above example 'napalm_logs.mda_provisioning', but we will get to it shortly. 
You need to note that the action is triggered with parameters that were delivered from syslog message. This would be the IOM/MDA slots and actual router IP/name that the cards were inserted to. There is more parms that comes together with syslog message or parms that can be added within napalm-logs at the time of syslog message transformation. It's really cool how easily you can use those params within stackstorm thanks to common json format.

Now, let's create './actions/pythonactions/' in my napalm_logs pack. That's the place where action files and action python scripts are kept. Action yaml file is called mda_provisioning.yaml, it's kept in './actions/' and it looks like this:

```
---
name: "mda_provisioning"
runner_type: "python-script"
description: "Provisioning of the MDA."
enabled: true
entry_point: "pythonactions/syslog_mda_runner.py"
pack: napalm_logs
parameters:
    hostname:
        type: "string"
        description: "hostname"
        required: true
    hostip:
        type: "string"
        description: "IP of the host"
        required: true
    mda_tag:
        type: "string"
        description: "MDA slot"
        required: true
```

The python script is called syslog_mda_runner.py, it's kept in './actions/pythonactions/' and it looks like this:

```
import re

from st2actions.runners.pythonrunner import Action
from SROSDriver import SROSDriver


class MdaRunner(Action):

    def run(self, hostname, hostip, mda_tag):
        self.iom_slot, self.mda_slot = self.get_slots(mda_tag)
        self.hostip = hostip
        check = self.iom_check()
        if check:
            cmd = '/show mda {}/{}'.format(self.iom_slot, self.mda_slot)
            show_mda_output = self.send_command(cmd)
            mda_sec = self.mda_section(show_mda_output)
            mda_type = self.get_mda_type(mda_sec)
            if mda_type:
                cmds = '/configure card {} mda ' \
                    '{} mda-type {}'.format(self.iom_slot, self.mda_slot, mda_type)
                self.send_command(cmds)
                show_mda_output = self.send_command(cmd)
                mda_sec = self.mda_section(show_mda_output)
                if not self._not_provisioned(mda_sec):
                    info = 'Router: {}; IOM: {}, ' \
                        'MDA: {}: TYPE: {}.'.format(hostname,
                            self.iom_slot, self.mda_slot, mda_type)
                    return(True, 'Successful provisioning of {}'.format(info))
                else:
                    return(False, 'Errors in provisioning.')
            else:
                return(False, 'Could not find MDA type.')
        else:
            return(False, check)

    def get_slots(self, mda_tag):
        try:
            iom, mda = mda_tag.split()[1].split('/')
        except Exception as f:
            print f
            return False
        else:
            return iom, mda

    def send_command(self, cmd):
        device = SROSDriver(self.hostip, 'admin', 'admin')
        device.open()
        result = device.command(cmd)
        device.close()
        return result

    def iom_check(self):
        cmd = '/show card {}'.format(self.iom_slot)
        s_card = self.send_command(cmd)
        if s_card:
            if 'up    up' in s_card:
                return True
            else:
                return 'nope {}'.format(s_card)
        else:
            return 'nope2 {}'.format(s_card)

    def get_mda_type(self, mda_sec):
        if self._not_provisioned(mda_sec) and self._different_equipped(mda_sec):
            mda_type = self._equipped_type(mda_sec)
            return mda_type

    def mda_section(self, show_mda_result):
        try:
            slot_mda = re.search(r'^(\d+\s+\d+)', show_mda_result, re.M).group(1)
            mda_start = show_mda_result.index(slot_mda)
            show_mda = show_mda_result[mda_start:]
        except Exception as f:
            print f
            return False
        else:
            mda_end = show_mda.index(re.search(r'(={79})', show_mda).group(1))
            return show_mda[:mda_end].strip()

    def _not_provisioned(self, mda_section):
        if re.search(r'(not provisioned)', mda_section):
            return True
        else:
            return False

    def _not_equipped(self, mda_section):
        if re.search(r'(not equipped)', mda_section):
            return True
        else:
            return False

    def _provision_type(self, mda_section):
        try:
            prov_type = re.search(r'\d+\s+\d+\s+(\S+)', mda_section).group(1)
        except Exception as f:
            print f
            return False
        else:
            return prov_type

    def _different_equipped(self, mda_section):
        try:
            mda_section.splitlines()[1]
        except Exception as f:
            print f
            return False
        else:
            return True

    def _equipped_type(self, mda_section):
        try:
            eq_line = mda_section.splitlines()[1]
            eq_type = re.search(r'\s+(\S+)', eq_line).group(1)
        except Exception as f:
            print f
            return False
        else:
            return eq_type
```

Script does pretty basic function - provisioning of the MDA card. But interesting thing here is that there is a level of validation before pushing any config to the node. Functions like iom_check() or _not_provisioned() are run, just to see if the state of the router is really appropriate to push MDA config. Also, recognition of the card type is done as we don't have this information from Syslog messages. Thanks to those couple of functions we are sure that Stackstorm will push config only in certain circumstances and that recognition is done automatically. If everything works as expected, we should get to the point where MDA cards are provisioned by Stackstorm whenever they are inserted into the router and provisioning was not done already.

We need to create our new action and rule by running:

```
st2 action create /opt/stackstorm/packs/napalm_logs/actions/mda_provisioning.yaml
st2 rule create /opt/stackstorm/packs/napalm_logs/rules/napalm_logs_mda.yaml
```

Both should be successfully created before testing our solution.

To test this example, I need to reboot my VM...

Now when our naplam-logs are running, when sensors, rules and actions are successfully registered/created, we just need to wait for a syslog event to be generated from the router...

Checking the triggers...

```
st2 trigger-instance list --trigger=naplam_logs.log
.
..
| 5ab50c429eb0c904913e74a7 | napalm_logs.log | Fri, 23 Mar 2018 14:16:34 UTC | processed         |
| 5ab50c459eb0c904913e74ab | napalm_logs.log | Fri, 23 Mar 2018 14:16:37 UTC | processed         |
| 5ab50c459eb0c904913e74ac | napalm_logs.log | Fri, 23 Mar 2018 14:16:37 UTC | processed         |
+--------------------------+-----------------+-------------------------------+-------------------+
```

We can see 3 syslog messages were received and 3 triggers were generated by sensor. However, if you check our rule definition above, you will see that we are only matching pattern related to MDA, not IOM. This means our rule should fire mda_provisioning action only 2 times in this case - 2 MDA insertions recognized. By checking execution list, we can prove it works as expected:

```
st2 execution list
.
..
| 5ab50c469eb0c904913e74b2 | core.local             | stanley      | succeeded (1s elapsed) | Fri, 23 Mar 2018       | Fri, 23 Mar 2018     |
|                          |                        |              |                        | 14:16:37 UTC           | 14:16:38 UTC         |
| 5ab50c469eb0c904913e74b7 | napalm_logs.mda_provis | stanley      | failed (4s elapsed)    | Fri, 23 Mar 2018       | Fri, 23 Mar 2018     |
|                          | ioning                 |              |                        | 14:16:38 UTC           | 14:16:42 UTC         |
| 5ab50c469eb0c904913e74b8 | napalm_logs.mda_provis | stanley      | succeeded (6s elapsed) | Fri, 23 Mar 2018       | Fri, 23 Mar 2018     |
|                          | ioning                 |              |                        | 14:16:38 UTC           | 14:16:44 UTC         |
+--------------------------+------------------------+--------------+------------------------+------------------------+----------------------+
+-------------------------------------------------------------------------------------------------------------------------------------------+

```

Stanley user is default Stackstorm user and that is how we see stackstorm fired actions automatically. We can see that there are only 2 executions of our mda_provisioning action which is exactly what we wanted.
Last thing to notice in the output is the fact that one execution of the mda_provisioning was successful and the other one failed. Why is that? 
Well our mda_provisioning action is not so dump and it performs some validation checks before pushing config. MDA 1/1 was operational and provisioned already. It was only spotted by our system because I had to reboot my VM to make my router send syslog event related to card insertion. This is actually good, because you can see that config is pushed not for IOM, not for MDA that is already provisioned, but only in case the config is really needed - MDA 1/2 in this example.

By checking the successful execution id you can verify which MDA was provisioned:

```
~$ st2 execution get 5ab50c469eb0c904913e74b8
id: 5ab50c469eb0c904913e74b8
status: succeeded (6s elapsed)
parameters: 
  hostip: 192.168.122.100
  hostname: R1
  mda_tag: Mda 1/2
result: 
  exit_code: 0
  result: 'Successful provisioning of Router: R1; IOM: 1, MDA: 2: TYPE: m5-1gb-sfp-b.'
  stderr: ''
  stdout: ''
```

and the output from the router:

```
A:R1# show mda 

===============================================================================
MDA Summary
===============================================================================
Slot  Mda   Provisioned Type                            Admin     Operational
                Equipped Type (if different)            State     State
-------------------------------------------------------------------------------
1     1     m5-1gb-sfp-b                                up        up
      2     m5-1gb-sfp-b                                up        up
===============================================================================
```

### Conclusion

Automate your network!!! :D


