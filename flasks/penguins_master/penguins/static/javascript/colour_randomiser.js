function getRandomCyanColour() {
  var colours = [ '#E0FFFF','#00FFFF','#00FFFF','#7FFFD4','#66CDAA','#AFEEEE',
                  '#40E0D0','#48D1CC','#00CED1','#20B2AA','#5F9EA0','#008B8B',
                  '#008080','#E0FFFF','#EBF4FA','#F0F8FF','#F0FFFF','#CCFFFF',
                  '#93FFE8','#9AFEFF','#7FFFD4','#00FFFF','#7DFDFE','#57FEFF',
                  '#8EEBEC','#50EBEC','#4EE2EC','#81D8D0','#92C7C7','#77BFC7',
                  '#78C7C7','#48CCCD','#43C6DB','#46C7C7','#7BCCB5','#43BFC7',
                  '#3EA99F','#3B9C9C','#438D80','#348781','#307D7E','#5E7D7E',
                  '#4C787E','#008080','#4E8975'
                ];
  var randomNumber = Math.floor(Math.random() * colours.length);
  var colour = colours[randomNumber]
  return colour;
}

function getRandomLightCyanColour() {
  var colours = [ '#E0FFFF','#AFEEEE','#ADD8E6','#B0E0E6','#F5FFFA','#F0FFFF',
                  '#F0F8FF','#F8F8FF'
                ];
  var randomNumber = Math.floor(Math.random() * colours.length);
  var colour = colours[randomNumber]
  return colour;
}

function getRandomOrangeColour() {
  var colours = [ '#FF7F50','#FF6347','#FF4500','#FFD700','#FFA500','#FF8C00',
                  '#FFE5B4','#FFDB58','#FFD801','#FDD017','#EAC117','#F2BB66',
                  '#FBB917','#FBB117','#FFA62F','#E9AB17','#E2A76F','#DEB887',
                  '#FFCBA4','#C9BE62','#E8A317','#EE9A4D','#C8B560','#D4A017',
                  '#C2B280','#C7A317','#C68E17','#B5A642','#ADA96E','#C19A6B',
                  '#CD7F32','#C88141','#C58917','#AF9B60','#AF7817','#B87333',
                  '#966F33','#806517','#827839','#827B60','#786D5F','#493D26',
                  '#483C32','#6F4E37','#835C3B','#7F5217','#7F462C','#C47451',
                  '#C36241','#C35817','#C85A17','#CC6600','#E56717','#E66C2C',
                  '#F87217','#F87431','#E67451','#FF8040','#F88017','#FF7F50',
                  '#F88158','#F9966B','#E78A61','#E18B6B','#E77471'
                ];
  var randomNumber = Math.floor(Math.random() * colours.length);
  var colour = colours[randomNumber]
  return colour;
}

function getRandomMixColour() {
  var colours = [ '#E0FFFF','#00FFFF','#00FFFF','#7FFFD4','#66CDAA','#AFEEEE',
                  '#40E0D0','#48D1CC','#00CED1','#20B2AA','#5F9EA0','#008B8B',
                  '#008080', '#FF7F50','#FF6347','#FF4500','#FFD700','#FFA500',
                  '#FF8C00'
                ];
  var randomNumber = Math.floor(Math.random() * colours.length);
  var colour = colours[randomNumber]
  return colour;
}
