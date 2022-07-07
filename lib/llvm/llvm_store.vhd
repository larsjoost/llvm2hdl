library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.memory_pkg.memory_master_t;
use work.memory_pkg.memory_slave_t;
use work.memory_pkg.memory_id_t;

entity llvm_store is
  port (
    clk     : in  std_ulogic;
    sreset  : in  std_ulogic;
    s_tvalid      : in std_ulogic;
    s_tready     : out std_ulogic;
    s_taddr    : in  std_ulogic_vector;
    s_tdata    : in  std_ulogic_vector;
    s_tag  : in  std_ulogic_vector;
    m_tag        : out std_ulogic_vector;
    m_tvalid     : out std_ulogic;
    m_tready     : in std_ulogic;
    m_memory : out memory_master_t;
    s_memory  : in  memory_slave_t
    );
end entity llvm_store;

architecture rtl of llvm_add is

    constant c_id_size : positive := 2 ** memory_id_t'length;
    type tag_storage_t is array (0 to c_id_size - 1) of 
        std_ulogic_vector(0 to s_tag'length - 1);

    signal tag_storage_i : tag_storage_t;
    signal data_transfer_i : std_ulogic;
    signal id_i : natural range 0 to c_id_size - 1 := 0;
begin

  s_tready <= (not m_memory.addr_valid or s_memory.addr_ready) and
  (not m_memory.data_valid or s_memory.data_ready);

data_transfer_i <= s_tvalid and s_tready;

  m_memory.data_width <= data'length;

  process (clk)
    variable id_v : memory_id_t;
  begin
    if rising_edge(clk) then
        if s_memory.addr_ready = '1' then
            m_memory.addr_valid <= '0';
        end if;
        if s_memory.data_ready = '1' then
            m_memory.data_valid <= '0';
        end if;
        if (data_transfer_i = '1') then
        m_memory.addr_valid <= '1';
        m_memory.addr <= memory_addr_t(resize(unsigned(address), m_memory.addr'length));
        id_v := std_ulogic_vector(to_unsigned(id_i, memory_id_t'length));
        m_memory.addr_id <= id_v;
        m_memory.data_valid <= '1';
        m_memory.data_id <= id_v;
        m_memory.data <= memory_data_t(resize(unsigned(data), m_memory.data'lenght));
        tag_storage_i(id_i) <= tag_in;
        end if;
    end if;
  end process;

  process (clk)
  begin
    if m_ready = '1' then
        m_valid <= '0';
    end if;
    if s_memory.data_response_valid = '1' and m_memory.data_response_ready = '1' then
        m_tag <= tag_storage_i(to_integer(unsigned(s_memory.data_response_id)));
        m_valid <= '1';
    end if;
  end process;

end architecture rtl;
