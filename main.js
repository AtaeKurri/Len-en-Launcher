const electron = require("electron");
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;

var mainWindow = null;

app.on(
    "window-all-closed",
    function()
    {
        {
            app.quit();
        }
    }
);

app.on(
    "ready",
    function()
    {
        var subpy = require('child_process').spawn('python', ['./app.py']);
        var rp = require("request-promise");
        var mainAddr = "http://localhost:5000";

        var OpenWindow = function()
        {
            mainWindow = new BrowserWindow({width: 800, height: 600, icon: 'static/images/icon.png'});
            mainWindow.setResizable(false)
            mainWindow.loadURL("http://localhost:5000");
            mainWindow.removeMenu()
            mainWindow.on(
                "closed",
                function()
                {
                    mainWindow = null;
                    subpy.kill("SIGINT");
                }
            );
        };

        var StartUp = function()
        {
            rp( mainAddr )
            .then(
                function( htmlString )
                {
                    console.log("server started!");
                    OpenWindow();
                }
            )
            .catch(
                function( err )
                {
                    console.log("waiting for the server start...");
                    // without tail call optimization this is a potential stack overflow
                    StartUp();
                }
            );
        };
        // fire!
        StartUp();
});