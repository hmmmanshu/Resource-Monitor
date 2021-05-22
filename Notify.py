def Notify(head, body, duration):
    import os
    if('nt' in os.name):
        from win10toast import ToastNotifier
        toast = ToastNotifier()
        toast.show_toast(head, body, duration=duration)
    else:
        pass