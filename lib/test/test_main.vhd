
entity test_main is
end entity test_main;

use std.env.finish;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.numeric_std.to_signed;
use ieee.numeric_std.to_integer;

architecture behavior of test_main is

  constant c_clock_period : time := 10 ns;

  constant tag_width : positive := 32;

  signal clk          : std_ulogic                            := '0';
  signal sreset       : std_ulogic;
  signal m_tdata  : std_ulogic_vector(0 to 0);
  signal s_tvalid : std_ulogic;
  signal s_tready : std_ulogic;
  signal m_tvalid : std_ulogic;
  signal m_tready : std_ulogic;
  signal s_tag    : std_ulogic_vector(0 to tag_width - 1);
  signal m_tag    : std_ulogic_vector(0 to tag_width - 1);
  
  signal tag_in       : std_ulogic_vector(0 to tag_width - 1) := (others => '0');
  signal tag_out      : std_ulogic_vector(0 to tag_width - 1);

begin

  entitymain_1 : entity work.entitymain
    port map (
      clk      => clk,
      sreset   => sreset,
      s_tvalid => s_tvalid,
      s_tready => s_tready,
      m_tdata  => m_tdata,
      m_tvalid => m_tvalid,
      m_tready => m_tready,
      s_tag    => s_tag,
      m_tag    => m_tag);
  
  clk <= not clk after c_clock_period/2;

  m_tready <= '1';

  s_tag <= (others => '0');
  
  process is
  begin  
    s_tvalid <= '0';
    wait until rising_edge(clk) and sreset = '0';
    s_tvalid <= '1';
    wait until rising_edge(clk) and m_tvalid = '1';
    assert (unsigned(m_tdata) = 0) 
    report "Test failed. m_tdata = " & to_string(m_tdata) & ", but expected 0" 
    severity failure;
    finish;
    wait;
  end process;

  process is
  begin
    sreset <= '1';
    wait for 2 * c_clock_period;
    wait until rising_edge(clk);
    sreset <= '0';
    wait;
  end process;

end architecture behavior;
