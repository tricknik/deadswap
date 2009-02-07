from sweetpotato.core import TaskAdapter
""" send an sms
"""
class sendsms(TaskAdapter):
    """ send an sms
    """
    def run(self):
        to = self.task.getProperty('to') 
        text = self.task.getProperty('text') 
        import gammu
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()
        message = {'Text': text, 'SMSC': {'Location': 1}, 'Number': to}
        sm.SendSMS(message)

