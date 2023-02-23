library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_fmul is
  port (
    clk      : in  std_ulogic;
    sreset   : in  std_ulogic;
    a        : in  std_ulogic_vector;
    b        : in  std_ulogic_vector;
    s_tag    : in  std_ulogic_vector;
    s_tvalid : in  std_ulogic;
    s_tready : out std_ulogic;
    m_tvalid : out std_ulogic;
    m_tready : in  std_ulogic;
    m_tag    : out std_ulogic_vector;
    m_tdata  : out std_ulogic_vector);
end entity llvm_fmul;

library ieee;
use ieee.float_pkg.all;

architecture rtl of llvm_fmul is

  signal a_i : float;
  signal b_i : float;
  signal q_i : float;

  signal s_tdata_i : std_ulogic_vector(0 to m_tdata'length - 1);

begin

  a_i <= to_float(a);

  b_i <= to_float(b);

  q_i <= a_i * b_i;

  s_tdata_i <= to_slv(q_i);

  llvm_buffer_1 : entity work.llvm_buffer(rtl)
    port map (
      clk      => clk,
      sreset   => sreset,
      s_tag    => s_tag,
      s_tvalid => s_tvalid,
      s_tready => s_tready,
      s_tdata  => s_tdata_i,
      m_tvalid => m_tvalid,
      m_tready => m_tready,
      m_tag    => m_tag,
      m_tdata  => m_tdata);

end architecture rtl;
