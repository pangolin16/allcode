var alphabet= "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
var i= 0;
var loopNo=0;
 function update(){document.getElementById("alpha").innerHTML=alphabet[i];i++;
   if(i==alphabet.length){i=0;
   loopNo++;
 }
 if (loopNo==1){
    var randomIndex=Math.floor(Math.random()*alphabet.length);
    var randomAlphabet=alphabet[randomIndex];
    document.getElementById("alpha").innerHTML=randomAlphabet;

clearInterval(intervalID);}
 }
 
 
 var intervalID=setInterval(update,100)




