library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_select is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    tag_in  : in  std_ulogic_vector;
    tag_out : out std_ulogic_vector;
    q       : out std_ulogic_vector;
    a       : in  std_ulogic_vector;
    b       : in  std_ulogic_vector;
    c       : in  std_ulogic_vector
    );
end entity llvm_select;

architecture rtl of llvm_select is

begin

  process (clk)
  begin
    if rising_edge(clk) then
      if (unsigned(a) = 0) then
        q <= c;
      else
        q <= b;
      end if;
      tag_out <= tag_in;
    end if;
  end process;

end architecture rtl;
