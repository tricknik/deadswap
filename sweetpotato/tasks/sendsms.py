from sweetpotato.core import TaskAdapter
""" send an sms
"""
import logging
class sendsms(TaskAdapter):
    """ send an sms
    """
    def run(self):
        to = self.task.getProperty('to') 
        text = self.task.getProperty('text') 
        message = {'Text': text, 'SMSC': {'Location': 1}, 'Number': to}
        import gammu
        sm = gammu.StateMachine()
        try:
            sm.ReadConfig()
            sm.Init()
            sm.SendSMS(message)
        except Exception as errors:
            for e in errors.args:
                self.task.log("Error %s in %s: %s" % (e["Code"],e["Where"],e["Text"]), logging.ERROR)
            raise SystemExit  
          

