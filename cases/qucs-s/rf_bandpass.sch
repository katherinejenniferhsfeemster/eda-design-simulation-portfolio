<Qucs Schematic 1.0.0>
<Properties>
  <View=0,0,1200,800,1,0,0>
  <Grid=10,10,1>
  <DataSet=rf_bandpass.dat>
  <DataDisplay=rf_bandpass.dpl>
  <OpenDisplay=1>
  <Script=rf_bandpass.m>
  <RunScript=0>
  <showFrame=0>
  <FrameText0=Title>
  <FrameText1=Drawn By: Katherine Feemster>
  <FrameText2=Date: 2026-04-24>
  <FrameText3=Revision: R1>
</Properties>
<Symbol>
</Symbol>
<Components>
  <Pac P1 1 150 350 18 -26 0 1 "1" 1 "50 Ohm" 1 "0 dBm" 0 "1 GHz" 0 "26.85" 0>
  <GND *  1 150 400 0 0 0 0>
  <L L1 1 270 280 -26 10 0 0 "22 nH" 1 "" 0>
  <C C1 1 370 280 -26 17 0 0 "470 pF" 1 "" 0>
  <L L2 1 470 350 10 -26 0 1 "22 nH" 1 "" 0>
  <C C2 1 470 280 -26 17 0 0 "470 pF" 1 "" 0>
  <Pac P2 1 620 350 18 -26 0 1 "2" 1 "50 Ohm" 1 "0 dBm" 0 "1 GHz" 0 "26.85" 0>
  <GND *  1 620 400 0 0 0 0>
  <.SP SP1 1 240 500 0 67 0 0 "log" 1 "10 MHz" 1 "100 MHz" 1 "401" 1 "no" 0 "1" 0 "2" 0>
  <Eqn Eqn1 1 500 500 -28 15 0 0 "S11=S[1,1]" 1 "S21=S[2,1]" 1 "yes" 0>
</Components>
<Wires>
  <150 280 270 280 "" 0 0 0 "">
  <150 320 150 350 "" 0 0 0 "">
  <150 280 150 320 "" 0 0 0 "">
  <270 280 370 280 "" 0 0 0 "">
  <370 280 470 280 "" 0 0 0 "">
  <470 280 470 350 "" 0 0 0 "">
  <470 350 620 350 "" 0 0 0 "">
  <620 350 620 350 "" 0 0 0 "">
</Wires>
<Diagrams>
  <Smith 550 400 250 250 3 #c0c0c0 1 10 1 0 4 1 1 1 1 1 1 0 1 1 0 0 315 0 225 "" "" "">
        <"rf_bandpass.dat/S11" #0000ff 0 3 0 0 0>
  </Smith>
  <Rect 900 300 300 200 3 #c0c0c0 1 10 1 1e7 1 1e8 1 -40 10 10 1 1 10 1 315 0 225 "" "" "">
        <"rf_bandpass.dat/dB(S21)" #ff7f00 0 3 0 0 0>
  </Rect>
</Diagrams>
<Paintings>
  <Text 130 120 24 #000000 0 "Sensor Frontend — RF Band-pass">
</Paintings>
