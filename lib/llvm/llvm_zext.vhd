library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.resize;
use ieee.numeric_std.to_unsigned;
use ieee.numeric_std.unsigned;

entity llvm_zext is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector;
    a       : in  std_ulogic_vector
    );
end entity llvm_zext;

architecture rtl of llvm_zext is

  signal a_i : unsigned(0 to a'length - 1);

begin

    q       <= std_ulogic_vector(resize(a_i, q'length));

    tag_out <= tag_in;

end architecture rtl;
