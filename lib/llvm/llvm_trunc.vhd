library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.resize;
use ieee.numeric_std.to_unsigned;
use ieee.numeric_std.unsigned;

entity llvm_trunc is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector;
    a       : in  std_ulogic_vector
    );
end entity llvm_trunc;

architecture rtl of llvm_trunc is

  signal a_i : std_ulogic_vector(a'length - 1 downto 0);

begin

  a_i <= a;

  q <= a_i(q'length - 1 downto 0);

  tag_out <= tag_in;

end architecture rtl;
