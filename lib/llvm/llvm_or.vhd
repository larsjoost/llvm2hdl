library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.numeric_std.resize;

entity llvm_or is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector;
    a       : in  std_ulogic_vector;
    b       : in  std_ulogic_vector
    );
end entity llvm_or;

architecture rtl of llvm_or is

  signal q_i : std_ulogic_vector(0 to a'length - 1);

begin

  q_i <= a or b;

  process (clk)
  begin
    if rising_edge(clk) then
      q <= std_ulogic_vector(resize(unsigned(q_i), q'length));
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;
