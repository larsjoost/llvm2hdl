library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity test_main is
end entity test_main;

use std.env.finish;

architecture behavior of test_main is

  constant c_clock_period : time := 10 ns;

  constant tag_width : positive := 1;

  signal return_value : std_ulogic_vector(0 to 32 - 1);
  signal clk          : std_ulogic                            := '0';
  signal sreset       : std_ulogic;
  signal tag_in       : std_ulogic_vector(0 to tag_width - 1) := (others => '0');
  signal tag_out      : std_ulogic_vector(0 to tag_width - 1);

begin

  entitymain_1 : entity work.entitymain
    port map (
      return_value => return_value,
      clk          => clk,
      sreset       => sreset,
      tag_in       => tag_in,
      tag_out      => tag_out);

  clk <= not clk after c_clock_period/2;

  process is
  begin  
    tag_in <= (others => '0');
    wait until rising_edge(clk) and sreset = '0';
    tag_in <= (others => '1');
    wait until rising_edge(clk) and tag_out(0) = '1';
    assert unsigned(return_value) = 0 report "Test failed" severity failure;
    finish;
    wait;
  end process;

  process is
  begin  -- process
    sreset <= '1';
    wait for 2 * c_clock_period;
    wait until rising_edge(clk);
    sreset <= '0';
    wait;
  end process;

end architecture behavior;
