library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity llvm_getelementptr is
  port (
    a         : in  std_ulogic_vector;
    offset    : in  std_ulogic_vector;
    -- Output port interface
    m_tdata   : out std_ulogic_vector;
    s_araddr  : in  std_ulogic_vector;
    s_arid    : in  std_ulogic_vector;
    s_arvalid : in  std_ulogic;
    s_arready : out std_ulogic;
    s_rdata   : out std_ulogic_vector;
    s_rid     : out std_logic_vector;
    s_rvalid  : out std_ulogic;
    s_rready  : in  std_ulogic;
    s_awaddr  : in  std_ulogic_vector;
    s_wready  : out std_ulogic;
    s_wvalid  : in  std_ulogic;
    s_wdata   : in  std_ulogic_vector;
    s_wid     : in  std_ulogic_vector;
    s_bready  : in  std_ulogic;
    s_bvalid  : out std_ulogic;
    s_bid     : out std_ulogic_vector;
    -- Argument pointer interface
    m_araddr  : out std_ulogic_vector;
    m_arid    : out std_ulogic_vector;
    m_arvalid : out std_ulogic;
    m_arready : in  std_ulogic;
    m_rdata   : in  std_ulogic_vector;
    m_rvalid  : in  std_ulogic;
    m_rready  : out std_ulogic;
    m_rid     : in  std_ulogic_vector;
    m_awaddr  : out std_ulogic_vector;
    m_wready  : in  std_ulogic;
    m_wvalid  : out std_ulogic;
    m_wdata   : out std_ulogic_vector;
    m_wid     : out std_ulogic_vector;
    m_bready  : out std_ulogic;
    m_bvalid  : in  std_ulogic;
    m_bid     : in  std_ulogic_vector;
    clk       : in  std_ulogic;
    sreset    : in  std_ulogic;
    s_tag     : in  std_ulogic_vector;
    s_tvalid  : in  std_ulogic;
    s_tready  : out std_ulogic;
    m_tvalid  : out std_ulogic;
    m_tready  : in  std_ulogic;
    m_tag     : out std_ulogic_vector);
end entity llvm_getelementptr;

architecture rtl of llvm_getelementptr is

  signal a_i : unsigned(0 to a'length - 1);
  signal q_i : unsigned(0 to m_tdata'length - 1);

  signal s_tdata_i : std_ulogic_vector(0 to m_tdata'length - 1);

begin

  a_i <= unsigned(a) + unsigned(offset);

  q_i <= a_i;

  s_tdata_i <= std_ulogic_vector(q_i);

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

  m_araddr  <= s_araddr;
  m_arid    <= s_arid;
  m_arvalid <= s_arvalid;
  s_arready <= m_arready;
  s_rdata   <= m_rdata;
  s_rvalid  <= m_rvalid;
  m_rready  <= s_rready;
  s_rid     <= m_rid;
  m_awaddr  <= s_awaddr;
  s_wready  <= m_wready;
  m_wvalid  <= s_wvalid;
  m_wdata   <= s_wdata;
  m_wid     <= s_wid;
  m_bready  <= s_bready;
  s_bvalid  <= m_bvalid;
  s_bid     <= m_bid;

end architecture rtl;
