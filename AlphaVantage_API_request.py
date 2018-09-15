import json
import requests
import pandas as pd
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.style.use('seaborn-deep')

# -------------- Parameters -------------- #    

data_start = 150000 
data_end = 203500
ticker = "MSFT"

refresh_frequency = 15 # Number of seconds between the API requests
maxApiError = 3 # Maximum connection errors allowed before the application-loop breaks
maxTimeError = 3 # Maximum timestamp errors allowed before the application-loop breaks
# -------------- E-mail -------------- #
'''
E-mail settings. Application sends an e-mail upon API errors.
'''
def send_error_email(message):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("youremail@gmail.com", "yourpassword")

    server.sendmail("sendfromemail@gmail.com", "targetemail@gmail.com", message)
    server.quit()

# -------------- Animation -------------- #

def animate_it():
    ax1.clear()
    ax1.plot(df['Close'].tail(5))

plt.ion() # Turn interactive mode on
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plt.title(ticker, 'close prices')
plt.show()

# -------------- App runtime -------------- #
current_time = int(datetime.datetime.now().strftime("%H%M%S"))
time_error_counter = [] # Time error container
api_error_counter = [] # API error container


while current_time > data_start and current_time < data_end:
    current_time = int(datetime.datetime.now().strftime("%H%M%S"))

    # Detect timestamp error
    if current_time < 25000:
        print("\n ERROR: Timestamp function malfunctioned.", current_time)
        time_error_counter.append(1)

        # Look for consecutive timestamp errors and halt app
        if sum(time_error_counter[:maxTimeError]) == maxTimeError:
            print(maxTimeError, ' consecutive time errors, application halted.')
            break
    else:
        time_error_counter.append(0)


    # API request and error handling    
    req = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&outputsize=compact&apikey=QT8A1SB5HLYGFVZR".format(symbol=ticker))
    content = json.loads(req.text)
    response_code = req.status_code # API response code

    # Detect invalid response code
    if response_code == 200:
        api_error_counter.append(0)
    else:    
        api_error_counter.append(1)
        print('ERROR: Response code: ', response_code)

        if sum(api_error_counter[:maxApiError]) == maxApiError:
            print(maxApiError, ' consecutive API errors, application halted.')
            send_error_email(maxApiError, ' consecutive API errors, application halted. API ERROR: ', response_code)
            break


    df = pd.DataFrame(content['Time Series (5min)'])
    df = df.T #Transpose

    # Rename columns
    df.columns = ['Open','High','Low','Close','Volume']
    print("\n Timestamp: ", current_time)
    print(df.tail(5))
    
    # Update the MPL plot
    animate_it()
    plt.pause(3)
    plt.draw()
    
    time.sleep(refresh_frequency)
    
