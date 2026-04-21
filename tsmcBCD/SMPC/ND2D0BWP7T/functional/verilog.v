// Created by ihdl
`timescale 1ns/1ps

`celldefine

module ND2D0BWP7T (A1, A2, ZN);
    input A1, A2;
    output ZN;
    nand		(ZN, A1, A2);

  specify
    (A1 => ZN) = (0, 0);
    (A2 => ZN) = (0, 0);
  endspecify
endmodule

`endcelldefine
