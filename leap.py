import sys
if sys.platform == "darwin":
    import OSX.Leap as Leap
elif 'linux' in sys.platform:
    import Linux.Leap as Leap
else:
    import Windows.Leap as Leap
