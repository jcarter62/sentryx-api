CREATE TABLE [dbo].[ami_data](
	[id] [varchar](50) NOT NULL,
	[meter_id] [varchar](25) NOT NULL,
	[reading_dt] [datetime] NOT NULL,
	[reading] [float] NOT NULL,
	[tstamp] [datetime] NOT NULL,
	[rec_id] [varchar](50) NULL,
	[data] [nchar](2048) NULL,
 CONSTRAINT [PK_ami_data] PRIMARY KEY CLUSTERED
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY];
ALTER TABLE [dbo].[ami_data] ADD  CONSTRAINT [DF_ami_data_rec_id]  DEFAULT ([dbo].[shortguid](newid())) FOR [id];

