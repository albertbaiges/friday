<p align="center">
  <img width="400" src="assets/fridayLogo.png">
</p>
<p align="center">
  <b>Web based python application to obtain location and sentiments of tweets </b>
</p>

![App Demo](readmeImage/resultsDemo.png)

## Installation
Fastest way to deploy this web application is by directly cloning [Friday Repository](https://github.com/albertbaiges/friday)  
Once installed, all dependencies of the webapp are listed in the requirements.txt file and can be easily installed in the Python enviromentby by running 

``` lang-zsh
  pip install -r requirements.txt
```

## Usage
To start the webapp it is only needed to execute the main.py file via

```
  python main.py
```
Then, the application will be running in the port of the host machine specified in the command line. You can direcly click on the URL to open the application on your browser.

Once Friday's homepage is opened it will be shown two boxes where it is need to introduce the desired parameters. In the left box you must introduce the keyword or the hashtag (#name) which you want to analyse. Whereas in the right box you must specify the number of tweets which will be analysed. Then just click on Submit and wait until the results are shown. The processing time will depend on the data introduced previously.

## Developers
* [Albert Baiges](https://github.com/albertbaiges)  
* [Sandra Rodriguez](https://github.com/SandraRoDiaz)
