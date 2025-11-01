export const SYMBOLS_SOURCE = "new,part,ks-base,1,path,M0 0 l-3.5 3.5," + 
                              "new,part,left-ghost,1,path,M1 -2.5 Q0 0 1 2.5," + 
                              "new,part,right-ghost,2,push-transform,scale(-1 1),use,left-ghost," + 
                              "new,drum,snare,3.5,0,0,3.5,1,use,ks-base,1,gsnare," +
                              "modifier,drum,explicit,snare_flam,4,0,0,3.5,1,path,M0 0 l-3.5 3.5 M-4 3.5 Q-4 1 -2.5 1,1,gsnare," +
                              "new,drum,kick,3.5,0,0,3.5,1,use,ks-base,0," + 
                              "modifier,drum,auto,ghost,2,+*drums,-kick,+1,0,+1,0,0,4,6,push-transform,\"translate(${parent_size_left} 0)\",use,left-ghost,pop-transform,push-transform,\"translate(${parent_size_right} 0)\",use,right-ghost,pop-transform,0," + 
                              "constraint,drum,gsnare,kick,10";

// TODO: add a decoration
