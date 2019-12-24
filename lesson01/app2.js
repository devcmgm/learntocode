var basePath = __dirname;
var http = require('http');
var fs = require('fs');

http.createServer(function (req, res) {
 
  filename = './indexchange.html';  

  console.log(req.url);

  fs.readFile(filename, function(err, data) {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write(data);
    res.end();
  });
}).listen(8080);
